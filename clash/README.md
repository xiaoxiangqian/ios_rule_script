# Clash / mihomo 规则集

把 `rule/Clash` 下按服务拆分的规则集，按目标策略合并成四个 `rule-provider`，
和 `qx/`、`v2rayn/` 同源、同步更新。

## 订阅链接

| 文件 | 内容 | 规则数 | 建议策略 |
| ---- | ---- | ---- | ---- |
| [Clash_01_Lan.yaml](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/clash/Clash_01_Lan.yaml) | 局域网、本地地址、优先直连的服务 | 407 | `DIRECT` |
| [Clash_02_Reject.yaml](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/clash/Clash_02_Reject.yaml) | 广告拦截 | 38,065 | `REJECT` |
| [Clash_03_Proxy.yaml](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/clash/Clash_03_Proxy.yaml) | 需要代理的服务 | 37,649 | 你的代理策略组 |
| [Clash_04_Direct.yaml](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/clash/Clash_04_Direct.yaml) | Apple、Microsoft、国内网站及流媒体 | 4,227 | `DIRECT` |

**四个要一起用**，文件名里的编号就是在 `rules` 里的书写顺序。跨文件已经去过重，
同一条规则只会出现在最靠前的那个文件里，所以顺序不能打乱。

## 配置

```yaml
rule-providers:
  bm7-lan:
    type: http
    behavior: classical
    format: yaml
    interval: 86400
    url: "https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/clash/Clash_01_Lan.yaml"
    path: ./ruleset/bm7-lan.yaml
  bm7-reject:
    type: http
    behavior: classical
    format: yaml
    interval: 86400
    url: "https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/clash/Clash_02_Reject.yaml"
    path: ./ruleset/bm7-reject.yaml
  bm7-proxy:
    type: http
    behavior: classical
    format: yaml
    interval: 86400
    url: "https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/clash/Clash_03_Proxy.yaml"
    path: ./ruleset/bm7-proxy.yaml
  bm7-direct:
    type: http
    behavior: classical
    format: yaml
    interval: 86400
    url: "https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/clash/Clash_04_Direct.yaml"
    path: ./ruleset/bm7-direct.yaml

rules:
  - RULE-SET,bm7-lan,DIRECT
  - RULE-SET,bm7-reject,REJECT
  - RULE-SET,bm7-proxy,PROXY
  - RULE-SET,bm7-direct,DIRECT
  - GEOIP,CN,DIRECT
  - MATCH,PROXY
```

把 `PROXY` 换成你自己的策略组名。`behavior` 必须是 `classical`，四个文件都混用了
域名和 IP 规则，`domain` 或 `ipcidr` 都装不下。

不想要广告拦截，去掉 `bm7-reject` 那一组和对应的 `RULE-SET` 行即可，其余三个照常工作。

## 为什么第一个文件要用 no-resolve

`Clash_01_Lan.yaml` 里的 IP 规则全部带 `no-resolve`。它排在最前面，如果不加，
每一个请求在匹配到这条之前都会先做一次 DNS 解析，开了 fake-ip 的话尤其伤。
后面三个文件不加，这样 IP 规则才能正常命中已解析的地址。

## 数据来源的一个坑

上游对大规则集做了拆分：`X.yaml` 只保留 DOMAIN-KEYWORD 和 IP 规则，域名被单独放进
`X_Domain.yaml`，完整的 classical 版本叫 `X_Classical.yaml`。比如 `China.yaml`
只有 30 条，而 `China_Classical.yaml` 有 3721 条。

生成脚本会优先取 `X_Classical.yaml`，没有才回退到 `X.yaml`（小规则集本身就是完整的）。
直接用 `X.yaml` 会让 China、Global、Proxy、广告这几个大集合悄悄丢掉九成以上的域名。

## 校验

每次生成后都会用真正的 mihomo 内核按上面的配置加载一遍：

```bash
python3 script/qxconf/check_clash.py <mihomo 可执行文件>
```

定时任务里也跑这一步，不通过就让任务失败，坏文件不会被提交。

## 自动更新

和 `qx/`、`v2rayn/` 共用一个生成脚本与定时任务，每天 03:00（UTC+8）自动重新生成，
详见 [qx/README.md](../qx/README.md#自动更新)。链接固定不变，
`interval: 86400` 会让 Clash 每天自己拉一次。
