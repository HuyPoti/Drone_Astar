# Drone_Astar

Dự án làm về sử dụng thuật toán A* có sử dụng thuật toán heuristic (ứng dụng trí tuệ nhân tạo) để chạy drone trong môi trường 3D thực tế dưới dạng bản đồ 2D

## Mục lục
* [Giới thiệu](#giới-thiệu)
* [Tính năng](#tính-năng)
* [Cài đặt](#cài-đặt)
* [Cách sử dụng](#cách-sử-dụng)
* [Cấu trúc dự án](#cấu-trúc-dự-án)
* [Liên hệ](#liên-hệ)

## Giới thiệu
* Ứng dụng giúp mô tả cách drone hoạt động thực tế, tìm đường đi tối ưu, tìm trạm sạc gần nhất và tim đường đi đến đích

## Tính năng
* Chọn hoặc random bản đồ
* Chạy demo drone
* Góc nhìn thứ ba

* Hiển thị đường đi đã đi
## Cài đặt
1.  **Clone repository:**
    ```bash
    git clone [https://github.com/HuyPoti/Drone_Astar.git](https://github.com/HuyPoti/Drone_Astar.git)
    cd Drone_Astar
    ```

2.  **Cài đặt các gói phụ thuộc:**
    ```bash
    pip install -r requirements.txt
    ```

## Cách sử dụng

Sau khi cài đặt thành công, bạn có thể truy cập ứng dụng thông qua cửa sổ hộp thoại pygame.

* **Choose Map:** Nhấp vào nút "Thêm tác vụ" và điền thông tin chi tiết.
    * Chọn bản đồ cần chạy
    * *Back* quay về bước ban đầu
* **Random Map:** Nhấp vào biểu tượng bút chì bên cạnh tác vụ để chỉnh sửa.
    * Chọn map cần chạy
    * *Back* quay về bước ban đầu
* **Instruction:** Hướng dẫn sử dụng chương trinh.
    * *Back* quay về bước ban đầu
* **Quit:** Thoát chương trình.

## Cấu trúc dự án
**Dự án gồm có 3 thư mục**
```
|
|--assets
|  |__... .png
|  |__Roboto-Medium.ttf
|--input
|  |__... .txt
|--src
|  |--gui
|  |  |__draw.py
|  |  |__menu.py
|  |--pathfinding
|  |  |__cell.py
|  |  |__pathfinder.py
|  |  |__utils.py
|  |__config.py
```
## Liên hệ
* Email liên hệ: khoahocgiahuy@gmail.com