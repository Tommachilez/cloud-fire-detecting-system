# 🔥 Hệ thống Phát hiện Cháy trên Nền tảng Đám mây

Dự án này triển khai một hệ thống phát hiện khói và lửa thời gian thực, tận dụng sự kết hợp mạnh mẽ giữa học máy và cơ sở hạ tầng đám mây. Hệ thống được thiết kế để xử lý các luồng video trực tiếp, xác định các nguy cơ hỏa hoạn tiềm ẩn bằng mô hình phát hiện đối tượng được huấn luyện tùy chỉnh và lưu trữ kết quả để phân tích và lưu trữ hồ sơ.

## 📜 Tổng quan Dự án

Cốt lõi của hệ thống này là một quy trình end-to-end tự động hóa việc phát hiện cháy. Các khung hình video được ghi lại và truyền vào một topic của **Confluent Kafka**. Một ứng dụng consumer, chạy trên một máy ảo đám mây, xử lý các khung hình này trong thời gian thực. Mỗi khung hình được gửi đến một mô hình **YOLOv11** được triển khai trên **Vertex AI của Google Cloud** để thực hiện suy luận. Khi mô hình phát hiện lửa hoặc khói với một mức độ tin cậy nhất định, nó sẽ vẽ các hộp giới hạn (bounding box) lên hình ảnh, sau đó hình ảnh này được tải lên **Google Cloud Storage (GCS)** để lưu trữ lâu dài và xem xét.

## 🏗️ Kiến trúc Hệ thống

Hệ thống được kiến trúc như một quy trình hướng sự kiện, có khả năng mở rộng:

1.  **Nguồn Video (Producer)**: Một thiết bị (như camera) ghi lại video và truyền từng khung hình dưới dạng tin nhắn đến một topic của Confluent Kafka.
2.  **Nhắn tin Thời gian thực (Confluent Kafka)**: Hoạt động như hệ thống thần kinh trung ương, tiếp nhận luồng khung hình video có thông lượng cao và cung cấp chúng cho các consumer.
3.  **Xử lý Thời gian thực (Consumer)**: Một script Python đăng ký vào topic Kafka. Nó tiêu thụ khung hình video mới nhất, giải mã và chuẩn bị cho việc phân tích.
4.  **Suy luận AI/ML (Google Vertex AI)**: Consumer gửi khung hình đến một endpoint của mô hình đã được triển khai trên Vertex AI. Mô hình sau khi được huấn luyện và xuất trọng số, nhóm sử dụng đóng gói container bằng docker, sau đó upload lên hệ thống của Vertex AI để tạo endpoint.
5.  **Trực quan hóa & Lưu trữ Kết quả (OpenCV & GCS)**: Nếu phát hiện lửa hoặc khói với ngưỡng tin cậy đã đặt, consumer sẽ sử dụng OpenCV để vẽ các hộp giới hạn và nhãn trực tiếp lên khung hình. Hình ảnh đã được chú thích này sau đó được lưu vào một bucket được chỉ định trong Google Cloud Storage với một dấu thời gian duy nhất.

## 🛠️ Công nghệ Cốt lõi

-   **Mô hình**: YOLOv11 (cụ thể là `yolov11n`) được tinh chỉnh để phát hiện lửa và khói.
-   **Ngôn ngữ lập trình**: Python
-   **Thư viện chính**:
    -   `ultralytics`: Để huấn luyện và xác thực mô hình YOLOv8.
    -   `confluent-kafka`: Client Python chính thức cho Apache Kafka.
    -   `google-cloud-aiplatform`: Để tương tác với các endpoint của Vertex AI.
    -   `google-cloud-storage`: Để lưu trữ đối tượng.
    -   `opencv-python`: Để xử lý hình ảnh và vẽ các hộp giới hạn.
    -   `numpy` & `base64`: Để thao tác và mã hóa dữ liệu.
-   **Nền tảng Đám mây**: Google Cloud Platform (GCP)
-   **Nền tảng Truyền phát**: Confluent Cloud cho Kafka

## Các nguồn quan trọng

- Bộ dữ liệu tự gán nhãn: <https://universe.roboflow.com/rimine/rimine_fire>
- Bộ dữ liệu huấn luyện: <https://www.kaggle.com/datasets/cookiecacheqq/fasdd-cv1>
