import time
import logging
import odrive
from odrive.utils import dump_errors

# 配置友好的日志输出，告别 ODrive 默认的静默报错
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SeedMango] %(levelname)s: %(message)s')

class SeedMangoSDK:
    def __init__(self, reduction_ratio=-30.0):
        """
        初始化 SeedMango 执行器 SDK
        :param reduction_ratio: 末端减速机速比，默认 -30.0 (55BM24 + 30:1 摆线减速器，负号抵消输出反向)
        """
        self.reduction_ratio = reduction_ratio
        self.odrv = None
        self.axis = None

    def connect(self, timeout=10):
        """
        连接底层的 ODrive 驱动器，将复杂的 find_any 黑盒化
        """
        logging.info("正在寻找 SeedMango 执行器，请确保 USB 数据线已连接且电源已打开 (15-48V)...")
        try:
            # 阻塞寻找电机，屏蔽底层复杂性
            self.odrv = odrive.find_any(timeout=timeout)
            self.axis = self.odrv.axis0
            
            # 获取硬件主次版本号，用于后续的底层兼容性判断
            hw_major = self.odrv.hw_version_major
            hw_minor = self.odrv.hw_version_minor
            logging.info(f"成功连接！检测到硬件版本: v{hw_major}.{hw_minor}")
            
            # 连接后默认清除一次历史错误，确保初始状态纯净
            self.clear_errors()
            return True
            
        except TimeoutError:
            logging.error("连接超时！请检查排障：")
            logging.error("1. 电源是否接反或未开启？(驱动器无防反接能力)")
            logging.error("2. 是否使用了仅能充电的 Type-C 线缆？")
            return False
        except Exception as e:
            logging.error(f"底层连接发生未知错误: {e}")
            return False

    def clear_errors(self):
        """
        一键清除所有报错，防止小白面对残留错误码不知所措
        """
        if not self._check_connection():
            return
        
        self.odrv.clear_errors() # 清除所有错误信息
        logging.info("已清空历史错误栈，电机重置为纯净状态。")

    def get_basic_status(self):
        """
        获取当前执行器的基础状态，用于快速自检
        """
        if not self._check_connection():
            return None
        
        # 读取总线电压与当前轴状态机
        voltage = self.odrv.vbus_voltage
        state = self.axis.current_state
        
        logging.info(f"系统自检 -> 总线电压: {voltage:.2f}V | 底层状态机码: {state}")
        
        return {
            "bus_voltage": voltage,
            "axis_state": state
        }

    def auto_calibrate(self):
        """
        全自动电机与编码器标定，屏蔽 ODrive 底层状态机复杂性
        """
        if not self._check_connection():
            return False

        logging.info("标定前准备：请将电机空载悬空，并固定好电机本体，确保转子可自由旋转。")

        # 注入 55BM24 电机安全参数，防止标定过流烧毁
        self.axis.motor.config.pole_pairs = 7
        self.axis.motor.config.torque_constant = 0.0719
        self.axis.motor.config.calibration_current = 2.0
        self.axis.motor.config.current_lim = 6.0
        logging.info("已注入 55BM24 电机安全配置：极对数7，限流6A")

        # 电机参数自识别
        logging.info("正在执行电机参数自识别 (Motor Calibration)...")
        self.axis.requested_state = 4

        while self.axis.current_state != 1:
            time.sleep(0.1)

        if self.axis.error != 0:
            logging.error(f"电机参数自识别失败，错误码: {self.axis.error}")
            dump_errors(self.odrv)
            return False

        logging.info("电机参数自识别完成。")

        # 编码器校准
        logging.info("正在执行编码器校准 (Encoder Offset Calibration)...")
        self.axis.requested_state = 7

        while self.axis.current_state != 1:
            time.sleep(0.1)

        if self.axis.error != 0:
            logging.error(f"编码器校准失败，错误码: {self.axis.error}")
            dump_errors(self.odrv)
            return False

        # 写入预校准标志位，下次上电可跳过标定
        self.axis.motor.config.pre_calibrated = 1
        self.axis.encoder.config.pre_calibrated = 1

        # save_configuration() 保存后驱动器会立即重启，导致 USB 断连并抛出
        # ObjectLostError，这是 ODrive 0.5.x 的正常行为，保存其实已生效，捕获即可
        try:
            self.odrv.save_configuration()
        except Exception as e:
            logging.info(f"保存后驱动器重启，连接已断开（正常现象）：{type(e).__name__}")

        logging.info("标定完成并保存。驱动器正在重启，请稍候 1~3 秒后重新 connect() 验证。")
        return True

    def set_mode(self, mode_name: str):
        """
        傻瓜式切换控制模式，黑盒化 ODrive control_mode / input_mode 配置
        :param mode_name: 'position' | 'velocity' | 'torque' | 'mit'
        """
        if not self._check_connection():
            return False

        # 切换前先请求空闲，确保安全
        self.axis.requested_state = 1

        if mode_name == 'position':
            self.axis.controller.config.control_mode = 3
            self.axis.controller.config.input_mode = 3
        elif mode_name == 'velocity':
            self.axis.controller.config.control_mode = 2
            self.axis.controller.config.input_mode = 2
        elif mode_name == 'torque':
            self.axis.controller.config.control_mode = 1
            self.axis.controller.config.input_mode = 1
        elif mode_name == 'mit':
            self.axis.controller.config.control_mode = 3
            self.axis.controller.config.input_mode = 9
        else:
            logging.error(f"未知的控制模式: '{mode_name}'，请使用 position / velocity / torque / mit")
            return False

        self.axis.requested_state = 8
        logging.info(f"已成功切换至控制模式: {mode_name}")
        return True

    def move_to(self, angle_degrees: float):
        """
        末端角度运动指令，自动完成减速比与方向换算
        :param angle_degrees: 目标末端角度 (度)
        """
        if not self._check_connection():
            return False

        if self.axis.current_state != 8:
            logging.warning("电机未处于闭环控制状态 (state=8)，请先调用 set_mode() 进入控制模式。")
            return False

        target_turns = (angle_degrees / 360.0) * self.reduction_ratio
        self.axis.controller.input_pos = target_turns
        logging.info(f"目标角度 {angle_degrees}° -> 换算电机圈数: {target_turns:.2f} turns")
        return True

    def get_encoder_status(self):
        """
        读取编码器输出，并换算成末端输出角度，便于反驱/手动转动时观察
        """
        if not self._check_connection():
            return None

        pos_rev = self.axis.encoder.pos_estimate      # 转子多圈位置，单位 rev(圈)
        vel_rev = self.axis.encoder.vel_estimate      # 转子速度，单位 rev/s
        shadow = self.axis.encoder.shadow_count       # 累计计数
        count_in_cpr = self.axis.encoder.count_in_cpr # 单圈内计数(0~cpr)

        # 换算末端角度：转子圈数 / 减速比 * 360
        output_deg = (pos_rev / self.reduction_ratio) * 360.0

        logging.info(
            f"编码器 -> 转子位置: {pos_rev:.4f} rev | 转子速度: {vel_rev:.3f} rev/s | "
            f"末端角度: {output_deg:.2f}° | shadow_count: {shadow} | count_in_cpr: {count_in_cpr}"
        )
        return {
            "rotor_pos_rev": pos_rev,
            "rotor_vel_rev_s": vel_rev,
            "output_angle_deg": output_deg,
            "shadow_count": shadow,
            "count_in_cpr": count_in_cpr,
        }

    def diagnose(self):
        """
        一键完整诊断：电压/电流、状态机、四类错误、温度、编码器、Q轴电流
        反驱时 LED 亮起就是电机发电，可用这个函数确认母线电压是否被顶高
        """
        if not self._check_connection():
            return None

        vbus = self.odrv.vbus_voltage
        ibus = self.odrv.ibus
        state = self.axis.current_state

        logging.info("==================== 执行器诊断 ====================")
        logging.info(f"母线电压 vbus: {vbus:.2f} V | 母线电流 ibus: {ibus:.3f} A | 状态机: {state}")

        # 温度（若使能了温度传感器则有效）
        try:
            fet_temp = self.axis.motor.fet_thermistor.temperature
            mot_temp = self.axis.motor.motor_thermistor.temperature
            logging.info(f"驱动板温度: {fet_temp:.1f}℃ | 电机温度: {mot_temp:.1f}℃")
        except Exception:
            logging.info("温度传感器未使能或不可读，跳过温度读取。")

        # Q轴电流（反映实际输出扭矩）
        try:
            iq_meas = self.axis.motor.current_control.Iq_measured
            logging.info(f"Q轴实测电流 Iq: {iq_meas:.3f} A")
        except Exception:
            pass

        self.get_encoder_status()

        # 打印四类错误
        dump_errors(self.odrv)
        logging.info("===================================================")

        return {"bus_voltage": vbus, "bus_current": ibus, "axis_state": state}

    def monitor(self, duration=10.0, interval=0.2):
        """
        实时监控：在指定时长内周期打印母线电压/电流与编码器位置
        反驱扭动输出端时运行它，可直观看到发电导致的电压变化和位置变化
        :param duration: 监控总时长（秒）
        :param interval: 采样间隔（秒）
        """
        if not self._check_connection():
            return False

        logging.info(f"开始实时监控 {duration}s（间隔 {interval}s），可用手转动输出端观察...")
        t_end = time.time() + duration
        while time.time() < t_end:
            vbus = self.odrv.vbus_voltage
            ibus = self.odrv.ibus
            pos_rev = self.axis.encoder.pos_estimate
            vel_rev = self.axis.encoder.vel_estimate
            output_deg = (pos_rev / self.reduction_ratio) * 360.0
            logging.info(
                f"vbus:{vbus:6.2f}V  ibus:{ibus:7.3f}A  转子:{pos_rev:8.3f}rev  "
                f"末端:{output_deg:7.2f}°  转速:{vel_rev:6.2f}rev/s"
            )
            time.sleep(interval)
        logging.info("监控结束。")
        return True

    def configure_brake_resistor(self, resistance_ohm: float):
        """
        配置并使能外接刹车（泄放）电阻，防止反驱/急停时反电动势顶高母线烧驱动器或电源
        接线：刹车电阻接在 5 针接口最上方两个焊孔 (EMG 和 GND) 之间（见说明书 2.4.7）
        :param resistance_ohm: 外接刹车电阻阻值（欧姆），如 2.0
        """
        if not self._check_connection():
            return False

        # 使能前必须处于空闲状态
        self.axis.requested_state = 1
        self.odrv.config.enable_brake_resistor = True
        self.odrv.config.brake_resistance = resistance_ohm
        # 保存后驱动器会重启并断连，捕获重启抛出的异常（正常现象）
        try:
            self.odrv.save_configuration()
        except Exception as e:
            logging.info(f"保存后驱动器重启，连接已断开（正常现象）：{type(e).__name__}")
        logging.info(f"已使能刹车电阻，阻值 {resistance_ohm}Ω，配置已保存（驱动器将重启，请稍后重新 connect()）。")
        return True

    def _check_connection(self):
        """内部防护机制：检查底层对象是否存在"""
        if self.odrv is None or self.axis is None:
            logging.warning("执行器未连接，请先调用 connect() 方法。")
            return False
        return True

# ==========================================
# 测试入口 (Hello World)
# ==========================================
if __name__ == "__main__":
    actuator = SeedMangoSDK()

    if actuator.connect():
        logging.info("准备开始自动化标定，请确保电机处于空载安全状态，3秒后开始...")
        time.sleep(3)

        if actuator.auto_calibrate():
            actuator.set_mode('position')
            actuator.move_to(90.0)
            time.sleep(2)
            actuator.move_to(0.0)
            logging.info("测试序列执行完毕！")