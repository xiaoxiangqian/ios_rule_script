#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用真正的 Xray 校验 v2rayn/ 下的规则集，确认能被内核加载。

生成器里的 check_v2rayn() 只能拦住已知的坏写法，这里直接把规则塞进一份
最小配置交给 Xray 自己判断，能覆盖没预料到的情况。

用法： python3 script/qxconf/check_v2rayn.py <xray 可执行文件> <geoip.dat 所在目录>
"""

import glob
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def make_config(ruleset_path, keep_disabled):
    """按 v2rayN 的用法把规则集包成一份可加载的 Xray 配置。

    keep_disabled=False 模拟 v2rayN 的正常行为（丢弃 enabled=false 的规则）；
    True 则模拟客户端不过滤、把说明行原样传给内核的最坏情况。
    """
    rules = json.load(open(ruleset_path, encoding="utf-8"))
    out = []
    for rule in rules:
        if not keep_disabled and rule.get("enabled") is False:
            continue
        drop = ("remarks",) if keep_disabled else ("remarks", "enabled")
        out.append({k: v for k, v in rule.items() if k not in drop})
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [{"tag": "socks", "port": 10808, "protocol": "socks",
                      "settings": {"udp": True}}],
        "outbounds": [{"tag": "proxy", "protocol": "freedom"},
                      {"tag": "direct", "protocol": "freedom"},
                      {"tag": "block", "protocol": "blackhole"}],
        "routing": {"domainStrategy": "IPIfNonMatch", "rules": out},
    }, len(out)


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    xray, asset_dir = sys.argv[1], sys.argv[2]
    env = dict(os.environ, XRAY_LOCATION_ASSET=asset_dir)

    files = sorted(glob.glob(os.path.join(ROOT, "v2rayn", "*.json")))
    if not files:
        raise SystemExit("v2rayn/ 下没有规则集")

    failed = False
    with tempfile.TemporaryDirectory() as tmp:
        for path in files:
            name = os.path.basename(path)
            for keep_disabled in (False, True):
                config, count = make_config(path, keep_disabled)
                config_path = os.path.join(tmp, "config.json")
                with open(config_path, "w", encoding="utf-8") as fp:
                    json.dump(config, fp, ensure_ascii=False)
                result = subprocess.run(
                    [xray, "run", "-test", "-config", config_path],
                    capture_output=True, text=True, env=env)
                mode = "含禁用行" if keep_disabled else "常规"
                if "Configuration OK" in result.stdout:
                    print(f"OK   {name}（{mode}，{count} 条规则）")
                else:
                    failed = True
                    tail = (result.stdout + result.stderr).strip().splitlines()[-1:]
                    print(f"FAIL {name}（{mode}）: {tail}")

    if failed:
        raise SystemExit("Xray 拒绝了生成的规则集")
    print("全部通过")


if __name__ == "__main__":
    main()
