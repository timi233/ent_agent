# 性能基线报告（2025-09-30）

- 后端端口：9003
- 接口：POST /api/v1/company/process/progressive
- 请求体：{"input_text":"测试企业","disable_cache":true,"enable_network":false}
- 采样次数：10
- 采集方法：curl -w time_total

## 结果
- P50: 1.764s
- P95: 2.869s

## 原始样本（http_code time_total）
参考 /tmp/perf_raw.txt，示例：
- #200 1.960539
- #200 2.429862
- #200 2.869256
- #200 1.910330
- #200 1.592084
- #200 1.480141
- #200 1.763712
- #200 1.951229
- #200 1.420678
- #200 1.734857

## 结论
- 当前 P50 ~1.76s，P95 ~2.87s，处于可接受范围，但仍有提升空间（网络与外部依赖关闭情况下）。

## 优化建议（Best Practices）
1. 端到端缓存与快速路径
   - progressive 路径已提供快速模式（disable_cache=true，enable_network=false）；建议为常见查询启用服务端一级缓存与聚合结果落盘，减少重复计算。
2. 依赖初始化与冷启动
   - 观察到首次请求较慢，建议在应用启动阶段预热关键依赖（如模型加载、连接池建立）。
3. 超时与重试策略
   - 客户端测试超时建议 ≥10s，服务端内部调用采用指数退避重试，避免瞬时抖动导致失败。
4. 监控与追踪
   - 为接口增加请求耗时、外部调用耗时分项日志（p50/p95/p99），结合trace区分瓶颈环节。

## 后续行动项
- [ ] 将集成性能测试从内嵌 ASGI 客户端改为直连运行实例，并提高超时至 10s，稳定测试（当前已部分处理，但两个用例仍需调整）
- [ ] 加入启动预热与缓存策略验证用例
- [ ] 在 CI 中加入每日性能基线采集与报告归档

## 复现命令
1) 采样 10 次并计算 P50/P95（保存原始数据）：
```
for i in $(seq 1 10); do curl -s -o /dev/null -w "#%{http_code} %{time_total}\n" \
  -X POST http://localhost:9003/api/v1/company/process/progressive \
  -H "Content-Type: application/json" \
  -d '{"input_text":"测试企业","disable_cache":true,"enable_network":false}'; done \
| tee /tmp/perf_raw.txt
```
2) 计算 P50/P95：
```
cut -d' ' -f2 /tmp/perf_raw.txt | sort -n > /tmp/perf_sorted.txt
awk '{a[NR]=$1} END{n=NR; mid=int((n+1)/2); p50=a[mid]; p95=a[int((n*0.95)+0.999)];
printf("P50(s)=%.3f\nP95(s)=%.3f\n", p50, p95)}' /tmp/perf_sorted.txt