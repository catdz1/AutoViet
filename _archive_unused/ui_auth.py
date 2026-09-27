# ui_auth.py — Nội dung XML của 2 file .ui: Login + Register
# Thêm vào file ui_strings.py hoặc import trực tiếp

LOGIN_UI = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>LoginDialog</class>
 <widget class="QDialog" name="LoginDialog">
  <property name="geometry">
   <rect><x>0</x><y>0</y><width>440</width><height>540</height></rect>
  </property>
  <property name="windowTitle"><string>AutoViet — Đăng nhập hệ thống</string></property>
  <property name="windowFlags">
   <set>Qt::Dialog|Qt::FramelessWindowHint</set>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="contentsMargins">
    <rect><left>0</left><top>0</top><right>0</right><bottom>0</bottom></rect>
   </property>
   <property name="spacing"><number>0</number></property>

   <!-- HEADER -->
   <item>
    <widget class="QWidget" name="header_widget">
     <layout class="QVBoxLayout" name="header_layout">
      <property name="contentsMargins">
       <rect><left>40</left><top>36</top><right>40</right><bottom>28</bottom></rect>
      </property>
      <property name="spacing"><number>8</number></property>
      <item>
       <widget class="QLabel" name="lbl_logo">
        <property name="text"><string>🚗  AutoViet</string></property>
        <property name="alignment"><set>Qt::AlignCenter</set></property>
       </widget>
      </item>
      <item>
       <widget class="QLabel" name="lbl_subtitle">
        <property name="text"><string>Hệ thống Quản lý Đại lý Xe Hơi v1.0</string></property>
        <property name="alignment"><set>Qt::AlignCenter</set></property>
       </widget>
      </item>
     </layout>
    </widget>
   </item>

   <!-- BODY -->
   <item>
    <widget class="QWidget" name="body_widget">
     <layout class="QVBoxLayout" name="body_layout">
      <property name="contentsMargins">
       <rect><left>40</left><top>0</top><right>40</right><bottom>32</bottom></rect>
      </property>
      <property name="spacing"><number>14</number></property>

      <!-- ROLE TAB -->
      <item>
       <widget class="QTabBar" name="tab_role">
        <property name="expanding"><bool>true</bool></property>
       </widget>
      </item>

      <item>
       <widget class="QLabel" name="lbl_role_notice">
        <property name="text"><string>Đăng nhập với tư cách Admin hoặc Nhân viên</string></property>
        <property name="alignment"><set>Qt::AlignCenter</set></property>
        <property name="wordWrap"><bool>true</bool></property>
       </widget>
      </item>

      <!-- USERNAME -->
      <item>
       <layout class="QVBoxLayout">
        <property name="spacing"><number>6</number></property>
        <item>
         <widget class="QLabel" name="lbl_username">
          <property name="text"><string>Tên đăng nhập</string></property>
         </widget>
        </item>
        <item>
         <widget class="QLineEdit" name="txt_username">
          <property name="placeholderText"><string>Nhập tên đăng nhập...</string></property>
         </widget>
        </item>
       </layout>
      </item>

      <!-- PASSWORD -->
      <item>
       <layout class="QVBoxLayout">
        <property name="spacing"><number>6</number></property>
        <item>
         <widget class="QLabel" name="lbl_password">
          <property name="text"><string>Mật khẩu</string></property>
         </widget>
        </item>
        <item>
         <widget class="QLineEdit" name="txt_password">
          <property name="placeholderText"><string>Nhập mật khẩu...</string></property>
          <property name="echoMode"><enum>QLineEdit::Password</enum></property>
         </widget>
        </item>
       </layout>
      </item>

      <!-- ERROR LABEL -->
      <item>
       <widget class="QLabel" name="lbl_error">
        <property name="text"><string></string></property>
        <property name="alignment"><set>Qt::AlignCenter</set></property>
       </widget>
      </item>

      <!-- LOGIN BUTTON -->
      <item>
       <widget class="QPushButton" name="btn_login">
        <property name="text"><string>🔓  Đăng nhập</string></property>
        <property name="minimumHeight"><number>44</number></property>
        <property name="default"><bool>true</bool></property>
       </widget>
      </item>

      <!-- REGISTER LINK -->
      <item>
       <widget class="QPushButton" name="btn_go_register">
        <property name="text"><string>Chưa có tài khoản? Đăng ký (Nhân viên)</string></property>
        <property name="flat"><bool>true</bool></property>
       </widget>
      </item>

      <!-- DEFAULT ADMIN HINT -->
      <item>
       <widget class="QLabel" name="lbl_hint">
        <property name="text"><string>  / </string></property>
        <property name="alignment"><set>Qt::AlignCenter</set></property>
       </widget>
      </item>

     </layout>
    </widget>
   </item>

  </layout>
 </widget>
 <resources/><connections/>
</ui>
"""

REGISTER_UI = """\
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>RegisterDialog</class>
 <widget class="QDialog" name="RegisterDialog">
  <property name="geometry">
   <rect><x>0</x><y>0</y><width>440</width><height>560</height></rect>
  </property>
  <property name="windowTitle"><string>AutoViet — Đăng ký tài khoản nhân viên</string></property>
  <property name="windowFlags">
   <set>Qt::Dialog|Qt::FramelessWindowHint</set>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <property name="contentsMargins">
    <rect><left>0</left><top>0</top><right>0</right><bottom>0</bottom></rect>
   </property>
   <property name="spacing"><number>0</number></property>

   <!-- HEADER -->
   <item>
    <widget class="QWidget" name="header_widget">
     <layout class="QVBoxLayout">
      <property name="contentsMargins">
       <rect><left>40</left><top>32</top><right>40</right><bottom>24</bottom></rect>
      </property>
      <property name="spacing"><number>8</number></property>
      <item>
       <widget class="QLabel" name="lbl_logo">
        <property name="text"><string>🚗  AutoViet</string></property>
        <property name="alignment"><set>Qt::AlignCenter</set></property>
       </widget>
      </item>
      <item>
       <widget class="QLabel" name="lbl_subtitle">
        <property name="text"><string>Tạo tài khoản nhân viên mới</string></property>
        <property name="alignment"><set>Qt::AlignCenter</set></property>
       </widget>
      </item>
     </layout>
    </widget>
   </item>

   <!-- BODY -->
   <item>
    <widget class="QWidget" name="body_widget">
     <layout class="QVBoxLayout" name="body_layout">
      <property name="contentsMargins">
       <rect><left>40</left><top>0</top><right>40</right><bottom>32</bottom></rect>
      </property>
      <property name="spacing"><number>12</number></property>

      <!-- HO TEN -->
      <item>
       <layout class="QVBoxLayout"><property name="spacing"><number>5</number></property>
        <item><widget class="QLabel" name="lbl_hoten"><property name="text"><string>Họ và tên *</string></property></widget></item>
        <item><widget class="QLineEdit" name="txt_hoten"><property name="placeholderText"><string>Nguyễn Văn A</string></property></widget></item>
       </layout>
      </item>

      <!-- USERNAME -->
      <item>
       <layout class="QVBoxLayout"><property name="spacing"><number>5</number></property>
        <item><widget class="QLabel" name="lbl_username"><property name="text"><string>Tên đăng nhập *</string></property></widget></item>
        <item><widget class="QLineEdit" name="txt_username"><property name="placeholderText"><string>Chỉ dùng chữ thường, số, dấu _</string></property></widget></item>
       </layout>
      </item>

      <!-- EMAIL -->
      <item>
       <layout class="QVBoxLayout"><property name="spacing"><number>5</number></property>
        <item><widget class="QLabel" name="lbl_email"><property name="text"><string>Email</string></property></widget></item>
        <item><widget class="QLineEdit" name="txt_email"><property name="placeholderText"><string>example@auto.vn</string></property></widget></item>
       </layout>
      </item>

      <!-- PASSWORD -->
      <item>
       <layout class="QVBoxLayout"><property name="spacing"><number>5</number></property>
        <item><widget class="QLabel" name="lbl_password"><property name="text"><string>Mật khẩu * (tối thiểu 6 ký tự)</string></property></widget></item>
        <item><widget class="QLineEdit" name="txt_password"><property name="placeholderText"><string>Nhập mật khẩu...</string></property><property name="echoMode"><enum>QLineEdit::Password</enum></property></widget></item>
       </layout>
      </item>

      <!-- CONFIRM PASSWORD -->
      <item>
       <layout class="QVBoxLayout"><property name="spacing"><number>5</number></property>
        <item><widget class="QLabel" name="lbl_confirm"><property name="text"><string>Xác nhận mật khẩu *</string></property></widget></item>
        <item><widget class="QLineEdit" name="txt_confirm"><property name="placeholderText"><string>Nhập lại mật khẩu...</string></property><property name="echoMode"><enum>QLineEdit::Password</enum></property></widget></item>
       </layout>
      </item>

      <!-- MA NV (optional) -->
      <item>
       <layout class="QVBoxLayout"><property name="spacing"><number>5</number></property>
        <item><widget class="QLabel" name="lbl_manv"><property name="text"><string>Mã nhân viên (nếu đã có)</string></property></widget></item>
        <item><widget class="QLineEdit" name="txt_manv"><property name="placeholderText"><string>VD: NV003 — để trống nếu chưa có</string></property></widget></item>
       </layout>
      </item>

      <!-- ERROR -->
      <item>
       <widget class="QLabel" name="lbl_error">
        <property name="text"><string></string></property>
        <property name="alignment"><set>Qt::AlignCenter</set></property>
        <property name="wordWrap"><bool>true</bool></property>
       </widget>
      </item>

      <!-- BUTTONS -->
      <item>
       <layout class="QHBoxLayout"><property name="spacing"><number>10</number></property>
        <item><widget class="QPushButton" name="btn_back"><property name="text"><string>← Quay lại</string></property></widget></item>
        <item>
         <widget class="QPushButton" name="btn_register">
          <property name="text"><string>✅  Đăng ký</string></property>
          <property name="minimumHeight"><number>44</number></property>
         </widget>
        </item>
       </layout>
      </item>

     </layout>
    </widget>
   </item>

  </layout>
 </widget>
 <resources/><connections/>
</ui>
"""
