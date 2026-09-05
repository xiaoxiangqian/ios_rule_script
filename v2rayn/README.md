# v2rayN / v2rayNG 路由规则集

把 `rule/QuantumultX` 下的分流规则转换成 v2rayN（以及 v2rayNG）能直接导入的路由规则集，
和 `qx/` 下的 Quantumult X 资源同源、同步更新。

## 订阅链接

| 文件 | 内容 | 域名数 | 大小 |
| ---- | ---- | ---- | ---- |
| [v2rayN_Rule_Lite.json](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/v2rayn/v2rayN_Rule_Lite.json) | 轻量分流 | 约 1.6 万 | 543 KB |
| [v2rayN_Rule_Full.json](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/v2rayn/v2rayN_Rule_Full.json) | 完整分流 | 约 4.1 万 | 1.3 MB |
| [v2rayN_Rule_Full_AdBlock.json](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/v2rayn/v2rayN_Rule_Full_AdBlock.json) | 完整分流 + 广告拦截 | 约 7.9 万 | 2.4 MB |

三选一即可，广告拦截已经并进第三个文件（v2rayN 一次只启用一个规则集，所以没有单独拆出来）。

## 怎么导入

设置 → 路由设置 → 勾选 **启用路由高级功能** → **高级功能** → **添加规则集** →
**从订阅 URL 中导入规则**，粘贴上面任意一条链接。

也可以先在浏览器打开链接，全选复制，然后选 **从剪贴板导入规则**。

出站标签用的是 v2rayN 的默认三个：`proxy` / `direct` / `block`，不需要额外配置。

## 规则顺序

自上而下匹配：

1. 局域网 IP（`geoip:private`）→ direct
2. 局域网、本地地址 → direct
3. 需要直连的常见服务 → direct
4. Telegram / AI / 流媒体 / 社交 / 开发者服务等 → proxy
5. Apple、Microsoft → direct
6. 国内流媒体、国内网站 → direct
7. `geoip:cn` → direct
8. 其余全部 → proxy

跨规则集重复的域名只保留最先出现的那一条。

## 转换说明

| Quantumult X | v2rayN |
| ---- | ---- |
| `HOST,a.b.c` | `full:a.b.c` |
| `HOST-SUFFIX,b.c` | `domain:b.c` |
| `HOST-KEYWORD,kw` | `kw`（Xray 中不带前缀即子串匹配） |
| `HOST-WILDCARD,a*.b` | `regexp:^a.*\.b$` |
| `IP-CIDR` / `IP6-CIDR` | `ip` 数组 |
| `USER-AGENT` | 丢弃 |
| `IP-ASN` | 丢弃 |

`USER-AGENT` 和 `IP-ASN` 在 Xray 路由里没有对应能力，每个文件丢弃约 167 条，
生成脚本会在输出里打印丢弃数量。

另外 v2rayN 的一条路由规则内 `domain` 和 `ip` 是**同时满足**的关系，
所以每个规则集都拆成了「域名」「IP」两条规则，不能手动合并。

上游数据里有 `::ffff:113.248.172.245/128` 这类 IPv4-mapped IPv6 地址，Xray 会把它
归一化成 4 字节 IPv4 再校验掩码，直接报 `invalid network mask for router: 128` 并
拒绝整份配置，所以生成时会还原成 `113.248.172.245/32`。

## 校验

每次生成后都会用真正的 Xray 内核加载一遍，确认配置能被接受：

```bash
python3 script/qxconf/check_v2rayn.py <xray 可执行文件> <geoip.dat 所在目录>
```

定时任务里也跑这一步，校验不过就让任务失败，坏文件不会被提交。

## 自动更新

和 `qx/` 共用一个生成脚本与定时任务，每天 03:00（UTC+8）自动重新生成，详见
[qx/README.md](../qx/README.md#自动更新)。链接固定不变。

v2rayN 不会自动重新拉取已导入的规则集，规则更新后需要重新导入一次；
如果你的版本支持规则集保存 URL 并手动刷新，用刷新即可。
