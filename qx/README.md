# Quantumult X 一键导入资源

把 `rule/QuantumultX` 下按服务拆分的几百个 `.list` 规则集，合并成少数几个可以直接填进
Quantumult X 的资源链接，用法与
`https://raw.githubusercontent.com/PaPerseller/chn-iplist/master/Quantumult(X)_noIP.conf`
完全一致：一条链接 = 一整套分流规则，配置里加一行 `[filter_remote]` 即可。

## 资源链接

> 下面的链接指向本仓库 `master` 分支，需要 PR 合并后才可用。
> 合并前请把链接里的 `master` 换成 `claude/quantumult-x-rules-conversion-jj9sgx`。
> 合并之后两种链接都有效：自动更新会把 master 和该分支一起推，所以已经填进
> Quantumult X 的分支链接不用改。

| 文件 | 内容 | 规则数 | 需要的策略 |
| ---- | ---- | ---- | ---- |
| [QuantumultX_Reject.conf](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/qx/QuantumultX_Reject.conf) | 广告拦截（AdvertisingLite） | 约 3.8 万 | 无，全部 `reject` |
| [QuantumultX_Rule_Lite.conf](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/qx/QuantumultX_Rule_Lite.conf) | 轻量分流：常用国外服务走代理，国内直连 | 约 1.9 万 | `Proxy` |
| [QuantumultX_Rule_Full.conf](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/qx/QuantumultX_Rule_Full.conf) | 完整分流：轻量版 + `Global` 规则集 | 约 4.3 万 | `Proxy` |
| [QuantumultX_Rule_Group.conf](https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/qx/QuantumultX_Rule_Group.conf) | 分组分流：按服务类型拆分策略 | 约 4.3 万 | `Proxy` `Streaming` `AI` `Telegram` `Apple` `Microsoft` `Google` |

三个分流文件任选其一，广告拦截可以叠加使用。

## 怎么用

### 方式一：直接编辑配置文件

在配置的 `[filter_remote]` 段里加上（以轻量版 + 广告拦截为例）：

```ini
[filter_remote]
https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/qx/QuantumultX_Reject.conf, tag=广告拦截, update-interval=86400, opt-parser=false, enabled=true
https://raw.githubusercontent.com/xiaoxiangqian/ios_rule_script/master/qx/QuantumultX_Rule_Lite.conf, tag=分流规则, update-interval=86400, opt-parser=false, enabled=true
```

再确认 `[policy]` 里存在文件所需的策略，例如：

```ini
[policy]
static=Proxy, proxy, direct, img-url=https://raw.githubusercontent.com/Koolson/Qure/master/IconSet/Color/Global.png
```

分组版则需要把 `Proxy`、`Streaming`、`AI`、`Telegram`、`Apple`、`Microsoft`、`Google`
这几个策略都建出来，名字必须一致。

### 方式二：在 App 内添加

Quantumult X → 设置 → 分流 → 右上角 `+` → 粘贴上面的链接 → 保存，然后在策略里
把资源里出现的策略名指向自己的节点或策略组。

## 规则顺序

Quantumult X 自上而下匹配，文件内的顺序是：

1. 局域网、本地地址 → `direct`
2. 需要直连的常见服务 → `direct`
3. Telegram / AI / 流媒体 / 社交 / 开发者服务等 → 代理
4. Apple、Microsoft → `direct`（分组版为独立策略，可自行改成代理）
5. 国内流媒体、国内网站 → `direct`
6. `GEOIP,CN,direct`
7. `FINAL,Proxy`

跨规则集重复的域名只保留最先出现的那一条，所以越靠前的规则集优先级越高。

`FINAL` 写在资源文件里主要是为了和参考文件保持一致，真正生效的兜底建议同时写在配置的
`[filter_local]` 末尾：

```ini
[filter_local]
geoip, cn, direct
final, Proxy
```

## 单个规则集

只想引用某一个服务的规则（比如只要 YouTube），见 [INDEX.md](INDEX.md)，里面列出了全部
686 个规则集的资源链接，配合 `force-policy=` 指定自己的策略即可：

```ini
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/QuantumultX/YouTube/YouTube.list, tag=YouTube, force-policy=Proxy, update-interval=86400, opt-parser=false, enabled=true
```

## v2rayN

同一套规则也转成了 v2rayN / v2rayNG 能导入的路由规则集，见 [v2rayn/README.md](../v2rayn/README.md)。

## 自动更新

规则数据来自 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)，
上游每日更新。`.github/workflows/update-qx.yml` 每天 **03:00（UTC+8）** 自动同步上游并重新生成
`qx/` 和 `v2rayn/` 下的文件，只有内容真的变化时才提交，所以订阅链接保持不变即可。

也可以在仓库 Actions 页面手动触发（workflow_dispatch），或在本地执行：

```bash
python3 script/qxconf/gen_qx_conf.py
```

改时间就改 workflow 里的 cron，注意 GitHub 的 cron 用 UTC：`0 19 * * *` 对应次日 03:00（UTC+8）。

需要增删规则集或调整策略映射，改 `script/qxconf/gen_qx_conf.py` 顶部的
`SIMPLE` / `GROUP` / `REJECT` 列表即可。
