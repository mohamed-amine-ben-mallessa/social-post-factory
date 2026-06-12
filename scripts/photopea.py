#!/usr/bin/env python3
"""
photopea.py — a tiny, dependency-free driver for the Photopea MCP server.

Photopea is a free, browser-based Photoshop. Its MCP server (npm:
`photopea-mcp-server`) exposes ~34 tools over stdio JSON-RPC. This helper spawns
the server, runs a list of tool calls, and returns the results — so you can design
images *programmatically* with zero install beyond Node + npx.

    from photopea import Photopea
    with Photopea() as pp:
        pp.call("photopea_create_document", {"width": 1080, "height": 1080, "fillColor": "#16182e"})
        pp.call("photopea_add_text", {"content": "Hello", "x": 80, "y": 200, "size": 96, "color": "#ffffff"})
        pp.call("photopea_export_image", {"outputPath": "out.png", "format": "png"})

Notes (verified the hard way):
- args use `content` (not text), `outputPath` (not path), shape bounds use {x,y,w,h}.
- the FIRST tool call opens a browser window — that's Photopea, it's expected.
- `photopea_run_script` runs raw Photopea JS; the script must end with app.echoToOE(...).

Stdlib only. Node + `npx` must be on PATH.
"""
from __future__ import annotations

import json
import subprocess
import threading
import time
from typing import Any, Optional


class PhotopeaError(Exception):
    pass


class Photopea:
    def __init__(self, *, server_cmd: Optional[list] = None, boot_timeout: int = 55,
                 call_timeout: int = 30):
        self.server_cmd = server_cmd or ["npx", "-y", "photopea-mcp-server"]
        self.boot_timeout = boot_timeout
        self.call_timeout = call_timeout
        self._proc: Optional[subprocess.Popen] = None
        self._results: dict[int, dict] = {}
        self._rid = 0
        self._started = False

    # context manager
    def __enter__(self) -> "Photopea":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    def start(self) -> None:
        self._proc = subprocess.Popen(
            self.server_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True,
        )
        threading.Thread(target=self._reader, daemon=True).start()
        self._send({"jsonrpc": "2.0", "id": self._next(),
                    "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                               "clientInfo": {"name": "photopea-as-code", "version": "1"}}})
        self._await(self._rid, self.boot_timeout)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self._started = True

    def stop(self) -> None:
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass

    # core
    def call(self, name: str, arguments: Optional[dict] = None, *,
             timeout: Optional[int] = None) -> Any:
        """Run one MCP tool. Returns the text payload; raises PhotopeaError on failure."""
        rid = self._next()
        self._send({"jsonrpc": "2.0", "id": rid, "method": "tools/call",
                    "params": {"name": name, "arguments": arguments or {}}})
        # first real call may still be booting the browser -> allow extra time
        r = self._await(rid, timeout or (self.boot_timeout if rid <= 2 else self.call_timeout))
        if r is None:
            raise PhotopeaError(f"{name}: timed out")
        if "error" in r:
            raise PhotopeaError(f"{name}: {r['error'].get('message', '')[:200]}")
        result = r.get("result", {})
        if result.get("isError"):
            content = result.get("content", [{}])
            raise PhotopeaError(f"{name}: {content[0].get('text', 'error')[:200]}")
        content = result.get("content", [])
        return content[0].get("text") if content else None

    def run_script(self, js: str, **kw) -> Any:
        """Run raw Photopea JS. Remember: end your script with app.echoToOE(...)."""
        return self.call("photopea_run_script", {"script": js}, **kw)

    def list_tools(self) -> list[str]:
        rid = self._next()
        self._send({"jsonrpc": "2.0", "id": rid, "method": "tools/list", "params": {}})
        r = self._await(rid, 20)
        return [t["name"] for t in (r or {}).get("result", {}).get("tools", [])]

    # plumbing
    def _next(self) -> int:
        self._rid += 1
        return self._rid

    def _send(self, msg: dict) -> None:
        assert self._proc and self._proc.stdin
        self._proc.stdin.write((json.dumps(msg) + "\n").encode())
        self._proc.stdin.flush()

    def _reader(self) -> None:
        assert self._proc and self._proc.stdout
        for raw in self._proc.stdout:
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "id" in o:
                self._results[o["id"]] = o

    def _await(self, rid: int, timeout: int) -> Optional[dict]:
        t0 = time.time()
        while rid not in self._results and time.time() - t0 < timeout:
            time.sleep(0.2)
        return self._results.get(rid)


# convenience helpers (the design primitives most projects reuse) ---------------

def gradient_bg(pp: Photopea, w: int, h: int, c1: str, c2: str, angle: int = 120,
                name: str = "Doc") -> None:
    pp.call("photopea_create_document", {"width": w, "height": h, "name": name, "fillColor": c1})
    pp.call("photopea_add_layer", {"name": "bg"})
    pp.call("photopea_add_gradient", {"target": "bg", "type": "linear",
                                      "colors": [c1, c2], "angle": angle})


def text(pp: Photopea, content: str, x: int, y: int, size: int, color: str,
         bold: bool = False, **extra) -> None:
    pp.call("photopea_add_text", {"content": content, "x": x, "y": y, "size": size,
                                  "color": color, "bold": bold, **extra})


def rect(pp: Photopea, x: int, y: int, w: int, h: int, color: str) -> None:
    # NB: bounds use x/y (not left/top)
    pp.call("photopea_add_shape", {"type": "rectangle",
                                   "bounds": {"x": x, "y": y, "width": w, "height": h},
                                   "fillColor": color})


def export(pp: Photopea, path: str, fmt: str = "png", quality: Optional[int] = None) -> None:
    args = {"outputPath": path, "format": fmt}
    if quality is not None and fmt == "jpg":
        args["quality"] = quality
    pp.call("photopea_export_image", args)
