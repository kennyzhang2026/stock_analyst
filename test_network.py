"""
网络诊断脚本
测试是否能访问AkShare的数据源
"""

import requests
import akshare as ak

print("=" * 60)
print("网络诊断测试")
print("=" * 60)

# 测试1: 基础网络连接
print("\n[测试1] 检查基础网络连接...")
try:
    response = requests.get("https://www.baidu.com", timeout=5)
    print(f"  ✓ 百度可以访问 (状态码: {response.status_code})")
except Exception as e:
    print(f"  ✗ 百度无法访问: {e}")

# 测试2: 东方财富网站
print("\n[测试2] 检查东方财富网站...")
try:
    response = requests.get("https://fund.eastmoney.com/", timeout=10)
    print(f"  ✓ 东方财富可以访问 (状态码: {response.status_code})")
except Exception as e:
    print(f"  ✗ 东方财富无法访问: {e}")
    print("  这可能是因为:")
    print("    - 网络环境限制（公司/学校网络）")
    print("    - 防火墙阻止")
    print("    - 需要配置代理")

# 测试3: AkShare接口
print("\n[测试3] 检查AkShare ETF接口...")
try:
    print("  正在获取ETF列表（可能需要10-30秒）...")
    df = ak.fund_etf_spot_em()
    print(f"  ✓ AkShare接口正常，获取到 {len(df)} 只ETF")
    # 查找513120
    target = df[df['代码'] == '513120']
    if not target.empty:
        print(f"  ✓ 找到513120: {target['名称'].values[0]}")
    else:
        print(f"  ✗ 未找到513120")
except Exception as e:
    print(f"  ✗ AkShare接口失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)

# 解决方案建议
print("\n如果上面测试失败，请尝试:")
print("1. 检查是否在公司/学校网络（可能有访问限制）")
print("2. 尝试使用手机热点网络")
print("3. 检查防火墙设置")
print("4. 如果需要代理，请告诉我代理地址")

input("\n按回车键退出...")
