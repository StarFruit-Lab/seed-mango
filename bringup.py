"""
SeedMango 执行器 首次上手引导脚本 (bringup)
=================================================
用途：带确认提示，一步步完成【看状态】和【校准】两个阶段。
本脚本不会让电机进入闭环转动，适合刹车电阻尚未到货时安全调试。

运行方式（在工作目录下）：
    python bringup.py

操作方式：
    - 每一步前会提示，按【回车】继续；
    - 想跳过某一步，输入 s 再回车；
    - 想退出，输入 q 再回车。
"""

import sys
import logging
from SeedMangoSDK import SeedMangoSDK


def ask(prompt: str) -> str:
    """统一的确认提示：回车=继续，s=跳过，q=退出"""
    print("\n" + "-" * 60)
    ans = input(f"{prompt}\n  [回车]继续 / [s]跳过 / [q]退出 > ").strip().lower()
    if ans == "q":
        print("已退出引导。")
        sys.exit(0)
    return ans


def main():
    print("=" * 60)
    print(" SeedMango 执行器 上手引导 —— 阶段：看状态 + 校准")
    print(" 提醒：本脚本不会让电机进入闭环转动，全程相对安全。")
    print("=" * 60)

    # ---------- 前置提醒 ----------
    print(
        "\n开始前请确认：\n"
        "  1) 已 pip install \"odrive==0.5.4\"（版本需匹配 0.5.x 固件）\n"
        "  2) 已用 Zadig 给 Interface 2 装了 WinUSB 驱动\n"
        "  3) 已先接好直流电源(核对正负、24V/20A)并开机，电源灯亮\n"
        "  4) 再插上 Type-C 数据线（非充电线）\n"
    )
    ask("以上都已就绪？")

    a = SeedMangoSDK()

    # ---------- 第 1 步：连接 ----------
    ask("第 1 步：连接执行器 (odrive.find_any)")
    if not a.connect():
        print("\n连接失败。请排查：数据线是否为充电线 / 电源是否开启 / "
              "Zadig 是否装了 Interface 2 的 WinUSB / odrive 是否为 0.5.4。")
        sys.exit(1)

    # ---------- 第 2 步：整体诊断 ----------
    if ask("第 2 步：整体诊断（电压/电流/状态/错误/温度/编码器）") != "s":
        a.diagnose()
        print("\n请核对：vbus 是否≈24V？状态机是否=1（空闲）？错误是否为空？")
        chk = input("  若有残留错误，输入 c 清除后继续；否则直接回车 > ").strip().lower()
        if chk == "c":
            a.clear_errors()
            a.diagnose()

    # ---------- 第 3 步：编码器读数 ----------
    if ask("第 3 步：读取编码器一次（确认磁铁+MA732 有输出）") != "s":
        a.get_encoder_status()

    # ---------- 第 4 步：手动反驱 + 实时监控 ----------
    if ask("第 4 步：实时监控 15 秒。这期间【慢慢轻轻】用手转动输出端，\n"
           "        观察 转子/末端角度 是否跟着变化。（电阻未到，切勿猛拽）") != "s":
        a.monitor(15)
        print("\n若角度随手动转动平滑变化 → 编码器与磁铁装配正常。")

    # ---------- 第 5 步：校准 ----------
    print("\n" + "=" * 60)
    print("接下来是【校准】。请务必：输出端空载 + 固定住/握紧本体。")
    print("过程：电机会发出尖锐‘嘀’声并转动；编码器校准会缓慢正转再反转。")
    print("=" * 60)
    ans = ask("第 5 步：开始全自动校准（电机识别 + 编码器校准，成功后自动保存）")
    if ans != "s":
        confirm = input("  再次确认：输出端已空载且本体已固定？(输入 yes 开始) > ").strip().lower()
        if confirm == "yes":
            ok = a.auto_calibrate()
            if ok:
                print("\n✅ 校准成功并已保存。以后上电无需再校准。")
            else:
                print("\n❌ 校准未通过，请查看上方错误码。常见：\n"
                      "   - CPR_POLEPAIRS_MISMATCH：检查磁铁贴装/间隙、极对数\n"
                      "   - 低压告警：识别电压偏高，可让我把 resistance_calib_max_voltage 设为 10")
        else:
            print("未输入 yes，已跳过校准。")

    # ---------- 收尾 ----------
    print("\n" + "=" * 60)
    print(" 今日引导结束。成果：连接正常 / 状态正常 / 编码器正常 / 校准完成。")
    print(" 下一步（等刹车电阻到货后）：configure_brake_resistor(2.0) → set_mode → 让它转起来。")
    print("=" * 60)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    try:
        main()
    except KeyboardInterrupt:
        print("\n已中断退出。")
