#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用真正的 mihomo 校验 clash/ 下的规则集，确认能被内核加载。

按 README 推荐的顺序把四个文件挂成 rule-provider，交给 mihomo 自己判断。

用法： python3 script/qxconf/check_clash.py <mihomo 可执行文件>
"""

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLASH_DIR = os.path.join(ROOT, "clash")

# 文件名 -> (provider 名, 策略)，顺序即 rules 里的书写顺序
LAYOUT = [
    ("Clash_01_Lan.yaml", "bm7-lan", "DIRECT"),
    ("Clash_02_Reject.yaml", "bm7-reject", "REJECT"),
    ("Clash_03_Proxy.yaml", "bm7-proxy", "PROXY"),
    ("Clash_04_Direct.yaml", "bm7-direct", "DIRECT"),
]

CONFIG = """mixed-port: 7890
mode: rule
log-level: silent
proxies: []
proxy-groups:
  - {{name: PROXY, type: select, proxies: [DIRECT]}}
rule-providers:
{providers}
rules:
{rules}
  - MATCH,PROXY
"""


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    mihomo = sys.argv[1]

    missing = [name for name, _, _ in LAYOUT
               if not os.path.isfile(os.path.join(CLASH_DIR, name))]
    if missing:
        raise SystemExit(f"缺少规则集：{missing}")

    with tempfile.TemporaryDirectory() as tmp:
        providers, rules, total = [], [], 0
        for name, tag, policy in LAYOUT:
            src = os.path.join(CLASH_DIR, name)
            shutil.copy(src, os.path.join(tmp, name))
            total += sum(1 for line in open(src, encoding="utf-8")
                         if line.strip().startswith("- "))
            providers.append(f"  {tag}: {{type: file, behavior: classical, "
                             f"format: yaml, path: ./{name}}}")
            rules.append(f"  - RULE-SET,{tag},{policy}")

        config_path = os.path.join(tmp, "config.yaml")
        with open(config_path, "w", encoding="utf-8") as fp:
            fp.write(CONFIG.format(providers="\n".join(providers),
                                   rules="\n".join(rules)))

        result = subprocess.run([mihomo, "-t", "-d", tmp, "-f", config_path],
                                capture_output=True, text=True)

    output = result.stdout + result.stderr
    if "test is successful" not in output.lower():
        print(output.strip()[-2000:])
        raise SystemExit("mihomo 拒绝了生成的规则集")
    print(f"OK   四个规则集共 {total} 条规则，mihomo 加载通过")


if __name__ == "__main__":
    main()
