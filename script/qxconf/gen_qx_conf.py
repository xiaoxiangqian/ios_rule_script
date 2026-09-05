#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 rule/QuantumultX 下的分流规则合并为可直接引用的订阅资源。

Quantumult X（qx/）：

- QuantumultX_Reject.conf       广告拦截，全部指向 reject
- QuantumultX_Rule_Lite.conf    轻量分流，仅需一个名为 Proxy 的策略
- QuantumultX_Rule_Full.conf    完整分流，额外并入 Global 规则集
- QuantumultX_Rule_Group.conf   多策略分组分流
- INDEX.md                      全部单个规则集的资源链接索引

v2rayN / v2rayNG（v2rayn/）：

- v2rayN_Rule_Lite.json         轻量分流
- v2rayN_Rule_Full.json         完整分流
- v2rayN_Rule_Full_AdBlock.json 完整分流 + 广告拦截

用法： python3 script/qxconf/gen_qx_conf.py
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import time

REPO = "blackmatrix7/ios_rule_script"
BRANCH = "master"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(ROOT, "rule", "QuantumultX")
OUT_DIR = os.path.join(ROOT, "qx")
V2RAY_DIR = os.path.join(ROOT, "v2rayn")

RAW_PREFIX = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/rule/QuantumultX"

# 单代理策略版：用户只需要在配置里准备一个名为 Proxy 的策略组。
SIMPLE = [
    ("Lan", "direct", "局域网及本地地址"),
    ("Direct", "direct", "常见需要直连的服务"),
    ("Telegram", "Proxy", "Telegram"),
    ("OpenAI", "Proxy", "OpenAI"),
    ("Claude", "Proxy", "Claude"),
    ("Gemini", "Proxy", "Gemini"),
    ("Copilot", "Proxy", "GitHub Copilot"),
    ("YouTube", "Proxy", "YouTube"),
    ("Netflix", "Proxy", "Netflix"),
    ("Disney", "Proxy", "Disney+"),
    ("Spotify", "Proxy", "Spotify"),
    ("TikTok", "Proxy", "TikTok"),
    ("Emby", "Proxy", "Emby"),
    ("AsianMedia", "Proxy", "亚洲流媒体"),
    ("GlobalMedia", "Proxy", "国际流媒体"),
    ("GitHub", "Proxy", "GitHub"),
    ("Twitter", "Proxy", "Twitter/X"),
    ("Facebook", "Proxy", "Facebook"),
    ("Instagram", "Proxy", "Instagram"),
    ("Discord", "Proxy", "Discord"),
    ("Whatsapp", "Proxy", "WhatsApp"),
    ("Line", "Proxy", "LINE"),
    ("PayPal", "Proxy", "PayPal"),
    ("Steam", "Proxy", "Steam"),
    ("Speedtest", "Proxy", "测速"),
    ("AppleProxy", "Proxy", "需要代理的 Apple 服务"),
    ("Proxy", "Proxy", "其他需要代理的服务"),
    ("Apple", "direct", "Apple"),
    ("Microsoft", "direct", "Microsoft"),
    ("ChinaMedia", "direct", "国内流媒体"),
    ("China", "direct", "国内网站及服务"),
]

# 完整版：在“其他需要代理的服务”之后并入体量较大的 Global 规则集。
FULL = []
for item in SIMPLE:
    FULL.append(item)
    if item[0] == "Proxy":
        FULL.append(("Global", "Proxy", "国外网站及服务"))

# 分组版：按服务类型拆分策略，方便分别落地。
GROUP = [
    ("Lan", "direct", "局域网及本地地址"),
    ("Direct", "direct", "常见需要直连的服务"),
    ("Telegram", "Telegram", "Telegram"),
    ("OpenAI", "AI", "OpenAI"),
    ("Claude", "AI", "Claude"),
    ("Gemini", "AI", "Gemini"),
    ("Copilot", "AI", "GitHub Copilot"),
    ("YouTube", "Streaming", "YouTube"),
    ("Netflix", "Streaming", "Netflix"),
    ("Disney", "Streaming", "Disney+"),
    ("Spotify", "Streaming", "Spotify"),
    ("TikTok", "Streaming", "TikTok"),
    ("Emby", "Streaming", "Emby"),
    ("AsianMedia", "Streaming", "亚洲流媒体"),
    ("GlobalMedia", "Streaming", "国际流媒体"),
    ("Google", "Google", "Google"),
    ("AppleProxy", "Apple", "需要代理的 Apple 服务"),
    ("Apple", "Apple", "Apple"),
    ("Microsoft", "Microsoft", "Microsoft"),
    ("GitHub", "Proxy", "GitHub"),
    ("Twitter", "Proxy", "Twitter/X"),
    ("Facebook", "Proxy", "Facebook"),
    ("Instagram", "Proxy", "Instagram"),
    ("Discord", "Proxy", "Discord"),
    ("Whatsapp", "Proxy", "WhatsApp"),
    ("Line", "Proxy", "LINE"),
    ("PayPal", "Proxy", "PayPal"),
    ("Steam", "Proxy", "Steam"),
    ("Speedtest", "Proxy", "测速"),
    ("Proxy", "Proxy", "其他需要代理的服务"),
    ("Global", "Proxy", "国外网站及服务"),
    ("ChinaMedia", "direct", "国内流媒体"),
    ("China", "direct", "国内网站及服务"),
]

REJECT = [
    ("AdvertisingLite", "reject", "广告拦截精简版"),
]

BUNDLES = [
    {
        "file": "QuantumultX_Reject.conf",
        "title": "广告拦截",
        "sections": REJECT,
        "tail": None,
        "note": "全部规则指向 reject，可与任意一个分流规则同时使用，建议放在分流规则之前。",
    },
    {
        "file": "QuantumultX_Rule_Lite.conf",
        "title": "分流规则 轻量版",
        "sections": SIMPLE,
        "tail": ("Proxy", "direct"),
        "note": "只需要在配置中准备一个名为 Proxy 的策略。未命中的国内地址由 GEOIP,CN 兜底直连。",
    },
    {
        "file": "QuantumultX_Rule_Full.conf",
        "title": "分流规则 完整版",
        "sections": FULL,
        "tail": ("Proxy", "direct"),
        "note": "在轻量版基础上并入 Global 规则集，命中率更高，体积也更大。同样只需要一个名为 Proxy 的策略。",
    },
    {
        "file": "QuantumultX_Rule_Group.conf",
        "title": "分流规则 分组版",
        "sections": GROUP,
        "tail": ("Proxy", "direct"),
        "note": "按服务类型拆分策略，需要在配置中准备 Proxy、Streaming、AI、Telegram、Apple、Microsoft、Google 这几个策略。",
    },
]


def read_rules(name):
    """读取一个规则集，返回 [(类型, 内容)]，忽略注释与空行。

    name 是相对 rule/QuantumultX 的目录，规则文件为同名的 .list，如
    ``YouTube`` 对应 ``YouTube/YouTube.list``，``Cloud/CloudCN`` 对应
    ``Cloud/CloudCN/CloudCN.list``。
    """
    path = os.path.join(SRC_DIR, name, f"{os.path.basename(name)}.list")
    rules = []
    with open(path, encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                continue
            rules.append((parts[0].upper(), parts[1]))
    return rules


def build(bundle):
    seen = set()
    sections = []
    total = 0
    for name, policy, desc in bundle["sections"]:
        lines = []
        for rule_type, value in read_rules(name):
            key = (rule_type, value.lower())
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"{rule_type},{value},{policy}")
        total += len(lines)
        sections.append((name, policy, desc, lines))

    policies = []
    for _, policy, _, lines in sections:
        if lines and policy not in policies:
            policies.append(policy)
    if bundle["tail"]:
        for policy in bundle["tail"]:
            if policy not in policies:
                policies.append(policy)

    out = [
        f"# NAME: {bundle['title']}",
        f"# SOURCE: https://github.com/{REPO}",
        f"# UPDATED: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC",
        f"# TOTAL: {total}",
        f"# POLICY: {', '.join(policies)}",
        f"# NOTE: {bundle['note']}",
        "",
    ]
    for name, policy, desc, lines in sections:
        out.append(f"# >>> {desc}（{name}，{len(lines)} 条）-> {policy}")
        out.extend(lines)
        out.append("")
    if bundle["tail"]:
        final_policy, geoip_policy = bundle["tail"]
        out.append("# >>> 兜底")
        out.append(f"GEOIP,CN,{geoip_policy}")
        out.append(f"FINAL,{final_policy}")
        out.append("")
    return "\n".join(out), total, policies


def write_index():
    names = []
    for current, dirs, files in os.walk(SRC_DIR):
        dirs.sort()
        base = os.path.basename(current)
        if f"{base}.list" in files:
            names.append(os.path.relpath(current, SRC_DIR).replace(os.sep, "/"))
    names.sort(key=str.lower)
    rows = []
    for name in names:
        count = len(read_rules(name))
        leaf = name.rsplit("/", 1)[-1]
        rows.append(f"| {name} | {count} | {RAW_PREFIX}/{name}/{leaf}.list |")
    body = [
        "# Quantumult X 单个规则集资源链接",
        "",
        f"本文件由 `script/qxconf/gen_qx_conf.py` 自动生成，共 {len(names)} 个规则集。",
        "",
        "每一条链接都可以直接填入 Quantumult X 的 `[filter_remote]`，例如：",
        "",
        "```",
        f"{RAW_PREFIX}/YouTube/YouTube.list, tag=YouTube, force-policy=Proxy, update-interval=86400, opt-parser=false, enabled=true",
        "```",
        "",
        "`force-policy` 会覆盖文件内自带的策略名，填写你自己配置里已存在的策略即可。",
        "",
        "| 规则集 | 规则数 | 资源链接 |",
        "| ---- | ---- | ---- |",
    ]
    body.extend(rows)
    body.append("")
    with open(os.path.join(OUT_DIR, "INDEX.md"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(body))
    return len(names)


# ---------------------------------------------------------------- v2rayN ----

# Quantumult X 的策略名 -> v2rayN 的 outboundTag
V2RAY_TAG = {"direct": "direct", "Proxy": "proxy", "reject": "block"}

# v2rayN 的路由规则里，同一条规则内 domain 与 ip 是“同时满足”的关系，
# 所以每个规则集要拆成域名、IP 两条规则。
V2RAY_BUNDLES = [
    {
        "file": "v2rayN_Rule_Lite.json",
        "title": "分流规则 轻量版",
        "sections": SIMPLE,
    },
    {
        "file": "v2rayN_Rule_Full.json",
        "title": "分流规则 完整版",
        "sections": FULL,
    },
    {
        "file": "v2rayN_Rule_Full_AdBlock.json",
        "title": "分流规则 完整版 + 广告拦截",
        "sections": REJECT + FULL,
    },
]


def wildcard_to_regexp(value):
    """HOST-WILDCARD 的 * 和 ? 转成 Xray 支持的正则。"""
    out = []
    for ch in value:
        if ch == "*":
            out.append(".*")
        elif ch == "?":
            out.append(".")
        else:
            out.append(re.escape(ch))
    return "regexp:^" + "".join(out) + "$"


def normalize_ip(value):
    """把 IP/CIDR 规范成 Xray 能接受的写法，无法处理时返回 None。

    上游数据里有 ``::ffff:113.248.172.245/128`` 这种 IPv4-mapped IPv6。
    Xray 会先把它归一化成 4 字节的 IPv4，再拿 /128 去校验掩码，直接报
    ``invalid network mask for router: 128`` 并拒绝整份配置，所以这里
    先还原成 IPv4 写法。
    """
    try:
        net = ipaddress.ip_network(value, strict=False)
    except ValueError:
        return None
    if net.version == 6:
        mapped = net.network_address.ipv4_mapped
        if mapped is not None:
            if net.prefixlen < 96:
                return None
            return f"{mapped}/{net.prefixlen - 96}"
    return value


def check_v2rayn(rules, where):
    """出厂自检：Xray 拒绝的写法一旦混进来就直接失败，不要生成坏文件。"""
    for rule in rules:
        for value in rule.get("ip", []):
            if value.startswith("geoip:"):
                continue
            net = ipaddress.ip_network(value, strict=False)
            if net.version == 6 and net.network_address.ipv4_mapped is not None:
                raise SystemExit(f"{where}: IPv4-mapped IPv6 未被转换：{value}")
        for domain in rule.get("domain", []):
            if domain.startswith("regexp:"):
                re.compile(domain[len("regexp:"):])


def to_v2ray(rule_type, value):
    """把一条 Quantumult X 规则转成 (字段, 值)；不支持的返回 None。

    字段为 "domain" 或 "ip"。USER-AGENT、IP-ASN 在 Xray 路由里没有对应能力，丢弃。
    """
    if rule_type == "HOST":
        return "domain", f"full:{value}"
    if rule_type == "HOST-SUFFIX":
        return "domain", f"domain:{value}"
    if rule_type == "HOST-KEYWORD":
        # Xray 里不带前缀的字符串就是子串匹配
        return "domain", value
    if rule_type == "HOST-WILDCARD":
        return "domain", wildcard_to_regexp(value)
    if rule_type in ("IP-CIDR", "IP6-CIDR"):
        normalized = normalize_ip(value)
        return ("ip", normalized) if normalized else None
    return None


def build_v2rayn(bundle):
    seen = set()
    emitted = set()
    rules = [
        {
            "remarks": f"{bundle['title']} | 生成于 "
                       f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC | "
                       f"https://github.com/{REPO}",
            "outboundTag": "direct",
            "domain": ["full:ruleset-info.invalid"],
            "enabled": False,
        },
        {"remarks": "局域网 IP", "outboundTag": "direct", "ip": ["geoip:private"], "enabled": True},
    ]
    kept = dropped = 0
    for name, policy, desc in bundle["sections"]:
        tag = V2RAY_TAG[policy]
        domains, ips = [], []
        for rule_type, value in read_rules(name):
            key = (rule_type, value.lower())
            if key in seen:
                continue
            seen.add(key)
            converted = to_v2ray(rule_type, value)
            if converted is None:
                dropped += 1
                continue
            if converted in emitted:
                continue
            emitted.add(converted)
            kept += 1
            (domains if converted[0] == "domain" else ips).append(converted[1])
        if domains:
            rules.append({"remarks": f"{desc}（{name}）域名", "outboundTag": tag,
                          "domain": domains, "enabled": True})
        if ips:
            rules.append({"remarks": f"{desc}（{name}）IP", "outboundTag": tag,
                          "ip": ips, "enabled": True})

    rules.append({"remarks": "中国大陆 IP 直连", "outboundTag": "direct",
                  "ip": ["geoip:cn"], "enabled": True})
    rules.append({"remarks": "其余流量走代理", "outboundTag": "proxy",
                  "port": "0-65535", "enabled": True})
    return rules, kept, dropped


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for bundle in BUNDLES:
        content, total, policies = build(bundle)
        path = os.path.join(OUT_DIR, bundle["file"])
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(content)
        print(f"{bundle['file']}: {total} 条规则，策略 {', '.join(policies)}")
    count = write_index()
    print(f"INDEX.md: {count} 个规则集")

    os.makedirs(V2RAY_DIR, exist_ok=True)
    for bundle in V2RAY_BUNDLES:
        rules, kept, dropped = build_v2rayn(bundle)
        check_v2rayn(rules, bundle["file"])
        path = os.path.join(V2RAY_DIR, bundle["file"])
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(rules, fp, ensure_ascii=False, indent=2)
            fp.write("\n")
        print(f"{bundle['file']}: {kept} 条规则，{len(rules)} 条路由，"
              f"丢弃 {dropped} 条（USER-AGENT / IP-ASN）")


if __name__ == "__main__":
    main()
