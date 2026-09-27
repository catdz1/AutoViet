"""
ui_strings.py
Chứa nội dung XML của tất cả file .ui Qt Designer
Được dùng bởi uic.loadUiType() hoặc lưu ra file .ui
"""

MAIN_WINDOW_UI = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry"><rect><x>0</x><y>0</y><width>1400</width><height>860</height></rect></property>
  <property name="minimumSize"><size><width>1280</width><height>760</height></size></property>
  <property name="windowTitle"><string>AutoViet — Hệ thống Quản lý Đại lý Xe Hơi v1.0</string></property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QHBoxLayout" name="main_layout">
    <property name="spacing"><number>0</number></property>
    <property name="contentsMargins"><rect><left>0</left><top>0</top><right>0</right><bottom>0</bottom></rect></property>
    <item>
     <widget class="QWidget" name="sidebar">
      <property name="minimumSize"><size><width>195</width><height>0</height></size></property>
      <property name="maximumSize"><size><width>195</width><height>16777215</height></size></property>
      <layout class="QVBoxLayout" name="sidebar_layout">
       <property name="spacing"><number>0</number></property>
       <property name="contentsMargins"><rect><left>0</left><top>0</top><right>0</right><bottom>0</bottom></rect></property>
       <item>
        <widget class="QWidget" name="logo_widget">
         <layout class="QVBoxLayout">
          <property name="contentsMargins"><rect><left>16</left><top>10</top><right>16</right><bottom>8</bottom></rect></property>
          <property name="spacing"><number>2</number></property>
          <item><widget class="QLabel" name="lbl_logo"><property name="text"><string>🚗  AutoViet</string></property></widget></item>
          <item><widget class="QLabel" name="lbl_logo_sub"><property name="text"><string>Quản lý đại lý xe hơi</string></property></widget></item>
         </layout>
        </widget>
       </item>
       <item><widget class="QFrame" name="line_logo"><property name="frameShape"><enum>QFrame::HLine</enum></property></widget></item>
       <item>
        <widget class="QTreeWidget" name="treeWidget">
         <property name="headerHidden"><bool>true</bool></property>
         <property name="indentation"><number>14</number></property>
         <column><property name="text"><string>Menu</string></property></column>
        </widget>
       </item>
      </layout>
     </widget>
    </item>
    <item>
     <widget class="QStackedWidget" name="stackedWidget">
      <widget class="QWidget" name="page_dashboard"/>
      <widget class="QWidget" name="page_xe"/>
      <widget class="QWidget" name="page_khach_hang"/>
      <widget class="QWidget" name="page_don_hang"/>
      <widget class="QWidget" name="page_nhan_vien"/>
      <widget class="QWidget" name="page_dich_vu"/>
      <widget class="QWidget" name="page_bao_cao"/>
     </widget>
    </item>
   </layout>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry"><rect><x>0</x><y>0</y><width>1400</width><height>30</height></rect></property>
   <widget class="QMenu" name="menu_file"><property name="title"><string>  Tệp  </string></property>
    <addaction name="action_backup"/><addaction name="separator"/><addaction name="action_exit"/>
   </widget>
   <widget class="QMenu" name="menu_manage"><property name="title"><string>  Quản lý  </string></property>
    <addaction name="action_xe"/><addaction name="action_kh"/><addaction name="action_dh"/>
    <addaction name="action_nv"/><addaction name="action_dv"/>
   </widget>
   <widget class="QMenu" name="menu_report"><property name="title"><string>  Báo cáo  </string></property>
    <addaction name="action_rpt_dt"/><addaction name="action_rpt_tk"/><addaction name="action_rpt_excel"/>
   </widget>
   <widget class="QMenu" name="menu_tools"><property name="title"><string>  Công cụ  </string></property>
    <addaction name="action_refresh"/>
   </widget>
   <widget class="QMenu" name="menu_help"><property name="title"><string>  Trợ giúp  </string></property>
    <addaction name="action_about"/>
   </widget>
   <addaction name="menu_file"/><addaction name="menu_manage"/>
   <addaction name="menu_report"/><addaction name="menu_tools"/><addaction name="menu_help"/>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
  <action name="action_backup"><property name="text"><string>💾 Sao lưu dữ liệu</string></property></action>
  <action name="action_exit"><property name="text"><string>🚪 Thoát</string></property><property name="shortcut"><string>Ctrl+Q</string></property></action>
  <action name="action_xe"><property name="text"><string>🚗 Danh sách xe</string></property></action>
  <action name="action_kh"><property name="text"><string>👥 Khách hàng</string></property></action>
  <action name="action_dh"><property name="text"><string>📋 Đơn hàng</string></property></action>
  <action name="action_nv"><property name="text"><string>🧑 Nhân viên</string></property></action>
  <action name="action_dv"><property name="text"><string>🔧 Dịch vụ</string></property></action>
  <action name="action_rpt_dt"><property name="text"><string>📊 Báo cáo doanh thu</string></property></action>
  <action name="action_rpt_tk"><property name="text"><string>📦 Báo cáo tồn kho</string></property></action>
  <action name="action_rpt_excel"><property name="text"><string>📤 Xuất Excel tổng hợp</string></property></action>
  <action name="action_refresh"><property name="text"><string>🔄 Làm mới</string></property><property name="shortcut"><string>F5</string></property></action>
  <action name="action_about"><property name="text"><string>ℹ Giới thiệu</string></property></action>
 </widget>
 <resources/><connections/>
</ui>
"""

XE_FORM_UI = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>XeDialog</class>
 <widget class="QDialog" name="XeDialog">
  <property name="geometry"><rect><x>0</x><y>0</y><width>520</width><height>600</height></rect></property>
  <property name="windowTitle"><string>Thêm / Sửa thông tin xe</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="contentsMargins"><rect><left>24</left><top>20</top><right>24</right><bottom>20</bottom></rect></property>
   <property name="spacing"><number>12</number></property>
   <item><widget class="QLabel" name="lbl_form_title"><property name="text"><string>THÔNG TIN XE HƠI</string></property><property name="objectName"><string>detail_key_form</string></property></widget></item>
   <item>
    <layout class="QFormLayout" name="formLayout">
     <property name="labelAlignment"><set>Qt::AlignRight|Qt::AlignVCenter</set></property>
     <property name="horizontalSpacing"><number>14</number></property><property name="verticalSpacing"><number>10</number></property>
     <item row="0" column="0"><widget class="QLabel"><property name="text"><string>Mã xe *</string></property></widget></item>
     <item row="0" column="1"><widget class="QLineEdit" name="txt_ma_xe"><property name="placeholderText"><string>VD: XE009</string></property></widget></item>
     <item row="1" column="0"><widget class="QLabel"><property name="text"><string>Hãng xe *</string></property></widget></item>
     <item row="1" column="1"><widget class="QLineEdit" name="txt_hang_xe"><property name="placeholderText"><string>Toyota, Honda, Kia...</string></property></widget></item>
     <item row="2" column="0"><widget class="QLabel"><property name="text"><string>Dòng xe *</string></property></widget></item>
     <item row="2" column="1"><widget class="QLineEdit" name="txt_dong_xe"><property name="placeholderText"><string>Camry, Civic, Sorento...</string></property></widget></item>
     <item row="3" column="0"><widget class="QLabel"><property name="text"><string>Năm SX *</string></property></widget></item>
     <item row="3" column="1"><widget class="QSpinBox" name="spin_nam_sx"><property name="minimum"><number>1990</number></property><property name="maximum"><number>2030</number></property><property name="value"><number>2024</number></property></widget></item>
     <item row="4" column="0"><widget class="QLabel"><property name="text"><string>Màu sắc</string></property></widget></item>
     <item row="4" column="1"><widget class="QLineEdit" name="txt_mau_sac"><property name="placeholderText"><string>Trắng Ngọc Trai, Đen Ánh Kim...</string></property></widget></item>
     <item row="5" column="0"><widget class="QLabel"><property name="text"><string>Số khung</string></property></widget></item>
     <item row="5" column="1"><widget class="QLineEdit" name="txt_so_khung"><property name="placeholderText"><string>Mã số khung (VIN)</string></property></widget></item>
     <item row="6" column="0"><widget class="QLabel"><property name="text"><string>Số máy</string></property></widget></item>
     <item row="6" column="1"><widget class="QLineEdit" name="txt_so_may"><property name="placeholderText"><string>Mã số máy xe</string></property></widget></item>
     <item row="7" column="0"><widget class="QLabel"><property name="text"><string>Giá nhập *</string></property></widget></item>
     <item row="7" column="1"><widget class="QDoubleSpinBox" name="spin_gia_nhap"><property name="maximum"><number>100000000000.0</number></property><property name="singleStep"><number>1000000.0</number></property><property name="decimals"><number>0</number></property><property name="suffix"><string> ₫</string></property></widget></item>
     <item row="8" column="0"><widget class="QLabel"><property name="text"><string>Giá bán *</string></property></widget></item>
     <item row="8" column="1"><widget class="QDoubleSpinBox" name="spin_gia_ban"><property name="maximum"><number>100000000000.0</number></property><property name="singleStep"><number>1000000.0</number></property><property name="decimals"><number>0</number></property><property name="suffix"><string> ₫</string></property></widget></item>
     <item row="9" column="0"><widget class="QLabel"><property name="text"><string>Tình trạng</string></property></widget></item>
     <item row="9" column="1"><widget class="QComboBox" name="cbo_tinh_trang"><item><property name="text"><string>Mới</string></property></item><item><property name="text"><string>Đã qua sử dụng</string></property></item></widget></item>
     <item row="10" column="0"><widget class="QLabel"><property name="text"><string>Trạng thái</string></property></widget></item>
     <item row="10" column="1"><widget class="QComboBox" name="cbo_trang_thai"><item><property name="text"><string>Còn hàng</string></property></item><item><property name="text"><string>Đặt cọc</string></property></item><item><property name="text"><string>Đã bán</string></property></item><item><property name="text"><string>Bảo dưỡng</string></property></item></widget></item>
     <item row="11" column="0"><widget class="QLabel"><property name="text"><string>Mô tả</string></property></widget></item>
     <item row="11" column="1"><widget class="QTextEdit" name="txt_mo_ta"><property name="maximumHeight"><number>70</number></property><property name="placeholderText"><string>Mô tả thêm về xe...</string></property></widget></item>
    </layout>
   </item>
   <item>
    <layout class="QHBoxLayout">
     <item><spacer><property name="orientation"><enum>Qt::Horizontal</enum></property><property name="sizeHint" stdset="0"><size><width>40</width><height>20</height></size></property></spacer></item>
     <item><widget class="QPushButton" name="btn_cancel"><property name="text"><string>Huỷ bỏ</string></property></widget></item>
     <item><widget class="QPushButton" name="btn_save"><property name="text"><string>💾  Lưu xe</string></property><property name="objectName"><string>btn_add</string></property><property name="default"><bool>true</bool></property></widget></item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections><connection><sender>btn_cancel</sender><signal>clicked()</signal><receiver>XeDialog</receiver><slot>reject()</slot><hints><hint type="sourcelabel"><x>20</x><y>20</y></hint><hint type="destinationlabel"><x>20</x><y>20</y></hint></hints></connection></connections>
</ui>
"""

KH_FORM_UI = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>KhachHangDialog</class>
 <widget class="QDialog" name="KhachHangDialog">
  <property name="geometry"><rect><x>0</x><y>0</y><width>480</width><height>460</height></rect></property>
  <property name="windowTitle"><string>Thêm / Sửa khách hàng</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="contentsMargins"><rect><left>24</left><top>20</top><right>24</right><bottom>20</bottom></rect></property>
   <property name="spacing"><number>12</number></property>
   <item><widget class="QLabel" name="lbl_title"><property name="text"><string>THÔNG TIN KHÁCH HÀNG</string></property><property name="objectName"><string>detail_key_form</string></property></widget></item>
   <item>
    <layout class="QFormLayout" name="formLayout">
     <property name="labelAlignment"><set>Qt::AlignRight|Qt::AlignVCenter</set></property>
     <property name="horizontalSpacing"><number>14</number></property><property name="verticalSpacing"><number>10</number></property>
     <item row="0" column="0"><widget class="QLabel"><property name="text"><string>Mã KH *</string></property></widget></item>
     <item row="0" column="1"><widget class="QLineEdit" name="txt_ma_kh"><property name="placeholderText"><string>VD: KH005</string></property></widget></item>
     <item row="1" column="0"><widget class="QLabel"><property name="text"><string>Họ tên *</string></property></widget></item>
     <item row="1" column="1"><widget class="QLineEdit" name="txt_ho_ten"><property name="placeholderText"><string>Họ và tên đầy đủ</string></property></widget></item>
     <item row="2" column="0"><widget class="QLabel"><property name="text"><string>Số điện thoại *</string></property></widget></item>
     <item row="2" column="1"><widget class="QLineEdit" name="txt_so_dt"><property name="placeholderText"><string>0912 345 678</string></property></widget></item>
     <item row="3" column="0"><widget class="QLabel"><property name="text"><string>Email</string></property></widget></item>
     <item row="3" column="1"><widget class="QLineEdit" name="txt_email"><property name="placeholderText"><string>example@email.com</string></property></widget></item>
     <item row="4" column="0"><widget class="QLabel"><property name="text"><string>Địa chỉ</string></property></widget></item>
     <item row="4" column="1"><widget class="QLineEdit" name="txt_dia_chi"><property name="placeholderText"><string>Số nhà, đường, quận, TP...</string></property></widget></item>
     <item row="5" column="0"><widget class="QLabel"><property name="text"><string>CMND/CCCD</string></property></widget></item>
     <item row="5" column="1"><widget class="QLineEdit" name="txt_cmnd"><property name="placeholderText"><string>Số CMND hoặc CCCD 12 số</string></property></widget></item>
     <item row="6" column="0"><widget class="QLabel"><property name="text"><string>Ngày sinh</string></property></widget></item>
     <item row="6" column="1"><widget class="QLineEdit" name="txt_ngay_sinh"><property name="placeholderText"><string>YYYY-MM-DD</string></property></widget></item>
     <item row="7" column="0"><widget class="QLabel"><property name="text"><string>Loại KH</string></property></widget></item>
     <item row="7" column="1"><widget class="QComboBox" name="cbo_loai_kh"><item><property name="text"><string>Cá nhân</string></property></item><item><property name="text"><string>Doanh nghiệp</string></property></item></widget></item>
     <item row="8" column="0"><widget class="QLabel"><property name="text"><string>Ghi chú</string></property></widget></item>
     <item row="8" column="1"><widget class="QTextEdit" name="txt_ghi_chu"><property name="maximumHeight"><number>60</number></property><property name="placeholderText"><string>Ghi chú thêm...</string></property></widget></item>
    </layout>
   </item>
   <item>
    <layout class="QHBoxLayout">
     <item><spacer><property name="orientation"><enum>Qt::Horizontal</enum></property><property name="sizeHint" stdset="0"><size><width>40</width><height>20</height></size></property></spacer></item>
     <item><widget class="QPushButton" name="btn_cancel"><property name="text"><string>Huỷ bỏ</string></property></widget></item>
     <item><widget class="QPushButton" name="btn_save"><property name="text"><string>💾  Lưu KH</string></property><property name="objectName"><string>btn_add</string></property><property name="default"><bool>true</bool></property></widget></item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections><connection><sender>btn_cancel</sender><signal>clicked()</signal><receiver>KhachHangDialog</receiver><slot>reject()</slot><hints><hint type="sourcelabel"><x>20</x><y>20</y></hint><hint type="destinationlabel"><x>20</x><y>20</y></hint></hints></connection></connections>
</ui>
"""

DH_FORM_UI = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>DonHangDialog</class>
 <widget class="QDialog" name="DonHangDialog">
  <property name="geometry"><rect><x>0</x><y>0</y><width>500</width><height>400</height></rect></property>
  <property name="windowTitle"><string>Tạo đơn hàng mới</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="contentsMargins"><rect><left>24</left><top>20</top><right>24</right><bottom>20</bottom></rect></property>
   <property name="spacing"><number>12</number></property>
   <item><widget class="QLabel" name="lbl_title"><property name="text"><string>THÔNG TIN ĐƠN HÀNG</string></property><property name="objectName"><string>detail_key_form</string></property></widget></item>
   <item>
    <layout class="QFormLayout" name="formLayout">
     <property name="labelAlignment"><set>Qt::AlignRight|Qt::AlignVCenter</set></property>
     <property name="horizontalSpacing"><number>14</number></property><property name="verticalSpacing"><number>10</number></property>
     <item row="0" column="0"><widget class="QLabel"><property name="text"><string>Mã đơn *</string></property></widget></item>
     <item row="0" column="1"><widget class="QLineEdit" name="txt_ma_don"/></item>
     <item row="1" column="0"><widget class="QLabel"><property name="text"><string>Xe *</string></property></widget></item>
     <item row="1" column="1"><widget class="QComboBox" name="cbo_xe"/></item>
     <item row="2" column="0"><widget class="QLabel"><property name="text"><string>Khách hàng *</string></property></widget></item>
     <item row="2" column="1"><widget class="QComboBox" name="cbo_kh"/></item>
     <item row="3" column="0"><widget class="QLabel"><property name="text"><string>Nhân viên *</string></property></widget></item>
     <item row="3" column="1"><widget class="QComboBox" name="cbo_nv"/></item>
     <item row="4" column="0"><widget class="QLabel"><property name="text"><string>Giá bán thực *</string></property></widget></item>
     <item row="4" column="1"><widget class="QDoubleSpinBox" name="spin_gia_ban"><property name="maximum"><number>100000000000.0</number></property><property name="singleStep"><number>1000000.0</number></property><property name="decimals"><number>0</number></property><property name="suffix"><string> ₫</string></property></widget></item>
     <item row="5" column="0"><widget class="QLabel"><property name="text"><string>Chiết khấu</string></property></widget></item>
     <item row="5" column="1"><widget class="QDoubleSpinBox" name="spin_ck"><property name="maximum"><number>100000000000.0</number></property><property name="singleStep"><number>1000000.0</number></property><property name="decimals"><number>0</number></property><property name="suffix"><string> ₫</string></property></widget></item>
     <item row="6" column="0"><widget class="QLabel"><property name="text"><string>Thanh toán</string></property></widget></item>
     <item row="6" column="1"><widget class="QComboBox" name="cbo_tt"><item><property name="text"><string>Tiền mặt</string></property></item><item><property name="text"><string>Vay ngân hàng</string></property></item><item><property name="text"><string>Trả góp</string></property></item></widget></item>
     <item row="7" column="0"><widget class="QLabel"><property name="text"><string>Ghi chú</string></property></widget></item>
     <item row="7" column="1"><widget class="QLineEdit" name="txt_ghi_chu"><property name="placeholderText"><string>Ghi chú thêm về đơn hàng...</string></property></widget></item>
    </layout>
   </item>
   <item>
    <layout class="QHBoxLayout">
     <item><spacer><property name="orientation"><enum>Qt::Horizontal</enum></property><property name="sizeHint" stdset="0"><size><width>40</width><height>20</height></size></property></spacer></item>
     <item><widget class="QPushButton" name="btn_cancel"><property name="text"><string>Huỷ bỏ</string></property></widget></item>
     <item><widget class="QPushButton" name="btn_save"><property name="text"><string>✅  Tạo đơn hàng</string></property><property name="objectName"><string>btn_add</string></property><property name="default"><bool>true</bool></property></widget></item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections><connection><sender>btn_cancel</sender><signal>clicked()</signal><receiver>DonHangDialog</receiver><slot>reject()</slot><hints><hint type="sourcelabel"><x>20</x><y>20</y></hint><hint type="destinationlabel"><x>20</x><y>20</y></hint></hints></connection></connections>
</ui>
"""

NV_FORM_UI = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>NhanVienDialog</class>
 <widget class="QDialog" name="NhanVienDialog">
  <property name="geometry"><rect><x>0</x><y>0</y><width>460</width><height>390</height></rect></property>
  <property name="windowTitle"><string>Thêm / Sửa nhân viên</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="contentsMargins"><rect><left>24</left><top>20</top><right>24</right><bottom>20</bottom></rect></property>
   <property name="spacing"><number>12</number></property>
   <item><widget class="QLabel" name="lbl_title"><property name="text"><string>THÔNG TIN NHÂN VIÊN</string></property><property name="objectName"><string>detail_key_form</string></property></widget></item>
   <item>
    <layout class="QFormLayout" name="formLayout">
     <property name="labelAlignment"><set>Qt::AlignRight|Qt::AlignVCenter</set></property>
     <property name="horizontalSpacing"><number>14</number></property><property name="verticalSpacing"><number>10</number></property>
     <item row="0" column="0"><widget class="QLabel"><property name="text"><string>Mã NV *</string></property></widget></item>
     <item row="0" column="1"><widget class="QLineEdit" name="txt_ma_nv"><property name="placeholderText"><string>VD: NV006</string></property></widget></item>
     <item row="1" column="0"><widget class="QLabel"><property name="text"><string>Họ tên *</string></property></widget></item>
     <item row="1" column="1"><widget class="QLineEdit" name="txt_ho_ten"><property name="placeholderText"><string>Họ và tên đầy đủ</string></property></widget></item>
     <item row="2" column="0"><widget class="QLabel"><property name="text"><string>Chức vụ *</string></property></widget></item>
     <item row="2" column="1"><widget class="QComboBox" name="cbo_chuc_vu"><item><property name="text"><string>Giám đốc</string></property></item><item><property name="text"><string>Quản lý BH</string></property></item><item><property name="text"><string>Nhân viên BH</string></property></item><item><property name="text"><string>Kỹ thuật viên</string></property></item><item><property name="text"><string>Kế toán</string></property></item></widget></item>
     <item row="3" column="0"><widget class="QLabel"><property name="text"><string>Số điện thoại</string></property></widget></item>
     <item row="3" column="1"><widget class="QLineEdit" name="txt_so_dt"><property name="placeholderText"><string>0912 345 678</string></property></widget></item>
     <item row="4" column="0"><widget class="QLabel"><property name="text"><string>Email</string></property></widget></item>
     <item row="4" column="1"><widget class="QLineEdit" name="txt_email"><property name="placeholderText"><string>nhanvien@auto.vn</string></property></widget></item>
     <item row="5" column="0"><widget class="QLabel"><property name="text"><string>Ngày vào làm</string></property></widget></item>
     <item row="5" column="1"><widget class="QLineEdit" name="txt_ngay_vao"><property name="placeholderText"><string>YYYY-MM-DD</string></property></widget></item>
     <item row="6" column="0"><widget class="QLabel"><property name="text"><string>Lương cơ bản</string></property></widget></item>
     <item row="6" column="1"><widget class="QDoubleSpinBox" name="spin_luong"><property name="maximum"><number>200000000.0</number></property><property name="singleStep"><number>500000.0</number></property><property name="decimals"><number>0</number></property><property name="suffix"><string> ₫</string></property></widget></item>
     <item row="7" column="0"><widget class="QLabel"><property name="text"><string>Trạng thái</string></property></widget></item>
     <item row="7" column="1"><widget class="QComboBox" name="cbo_trang_thai"><item><property name="text"><string>Đang làm</string></property></item><item><property name="text"><string>Thử việc</string></property></item><item><property name="text"><string>Nghỉ việc</string></property></item></widget></item>
    </layout>
   </item>
   <item>
    <layout class="QHBoxLayout">
     <item><spacer><property name="orientation"><enum>Qt::Horizontal</enum></property><property name="sizeHint" stdset="0"><size><width>40</width><height>20</height></size></property></spacer></item>
     <item><widget class="QPushButton" name="btn_cancel"><property name="text"><string>Huỷ bỏ</string></property></widget></item>
     <item><widget class="QPushButton" name="btn_save"><property name="text"><string>💾  Lưu NV</string></property><property name="objectName"><string>btn_add</string></property><property name="default"><bool>true</bool></property></widget></item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections><connection><sender>btn_cancel</sender><signal>clicked()</signal><receiver>NhanVienDialog</receiver><slot>reject()</slot><hints><hint type="sourcelabel"><x>20</x><y>20</y></hint><hint type="destinationlabel"><x>20</x><y>20</y></hint></hints></connection></connections>
</ui>
"""

DV_FORM_UI = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>DichVuDialog</class>
 <widget class="QDialog" name="DichVuDialog">
  <property name="geometry"><rect><x>0</x><y>0</y><width>480</width><height>360</height></rect></property>
  <property name="windowTitle"><string>Lập phiếu dịch vụ bảo dưỡng</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="contentsMargins"><rect><left>24</left><top>20</top><right>24</right><bottom>20</bottom></rect></property>
   <property name="spacing"><number>12</number></property>
   <item><widget class="QLabel" name="lbl_title"><property name="text"><string>PHIẾU DỊCH VỤ BẢO DƯỠNG</string></property><property name="objectName"><string>detail_key_form</string></property></widget></item>
   <item>
    <layout class="QFormLayout" name="formLayout">
     <property name="labelAlignment"><set>Qt::AlignRight|Qt::AlignVCenter</set></property>
     <property name="horizontalSpacing"><number>14</number></property><property name="verticalSpacing"><number>10</number></property>
     <item row="0" column="0"><widget class="QLabel"><property name="text"><string>Mã phiếu *</string></property></widget></item>
     <item row="0" column="1"><widget class="QLineEdit" name="txt_ma_dv"/></item>
     <item row="1" column="0"><widget class="QLabel"><property name="text"><string>Xe</string></property></widget></item>
     <item row="1" column="1"><widget class="QComboBox" name="cbo_xe"/></item>
     <item row="2" column="0"><widget class="QLabel"><property name="text"><string>Khách hàng</string></property></widget></item>
     <item row="2" column="1"><widget class="QComboBox" name="cbo_kh"/></item>
     <item row="3" column="0"><widget class="QLabel"><property name="text"><string>Nhân viên KTV</string></property></widget></item>
     <item row="3" column="1"><widget class="QComboBox" name="cbo_nv"/></item>
     <item row="4" column="0"><widget class="QLabel"><property name="text"><string>Loại dịch vụ *</string></property></widget></item>
     <item row="4" column="1"><widget class="QComboBox" name="cbo_loai"><item><property name="text"><string>Bảo dưỡng định kỳ</string></property></item><item><property name="text"><string>Sửa chữa</string></property></item><item><property name="text"><string>Đăng kiểm</string></property></item><item><property name="text"><string>Khác</string></property></item></widget></item>
     <item row="5" column="0"><widget class="QLabel"><property name="text"><string>Mô tả công việc</string></property></widget></item>
     <item row="5" column="1"><widget class="QLineEdit" name="txt_mo_ta"><property name="placeholderText"><string>Thay dầu, lọc gió, kiểm tra phanh...</string></property></widget></item>
     <item row="6" column="0"><widget class="QLabel"><property name="text"><string>Chi phí ước tính</string></property></widget></item>
     <item row="6" column="1"><widget class="QDoubleSpinBox" name="spin_chi_phi"><property name="maximum"><number>100000000.0</number></property><property name="singleStep"><number>50000.0</number></property><property name="decimals"><number>0</number></property><property name="suffix"><string> ₫</string></property></widget></item>
    </layout>
   </item>
   <item>
    <layout class="QHBoxLayout">
     <item><spacer><property name="orientation"><enum>Qt::Horizontal</enum></property><property name="sizeHint" stdset="0"><size><width>40</width><height>20</height></size></property></spacer></item>
     <item><widget class="QPushButton" name="btn_cancel"><property name="text"><string>Huỷ bỏ</string></property></widget></item>
     <item><widget class="QPushButton" name="btn_save"><property name="text"><string>🔧  Lập phiếu</string></property><property name="objectName"><string>btn_add</string></property><property name="default"><bool>true</bool></property></widget></item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections><connection><sender>btn_cancel</sender><signal>clicked()</signal><receiver>DichVuDialog</receiver><slot>reject()</slot><hints><hint type="sourcelabel"><x>20</x><y>20</y></hint><hint type="destinationlabel"><x>20</x><y>20</y></hint></hints></connection></connections>
</ui>
"""
