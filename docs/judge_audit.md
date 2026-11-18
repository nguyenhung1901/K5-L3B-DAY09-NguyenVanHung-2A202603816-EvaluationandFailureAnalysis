# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có | Dùng cho tiêu chí giọng điệu, không chấm tiền/approval |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không | Loại khỏi gate do bỏ sót nhiều FAIL |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | H-008 | PASS | FAIL | Người | Xưng "em" và "nha" suồng sã; bổ sung ví dụ giọng điệu không phù hợp. |
| 2 | H-029 | PASS | FAIL | Người | "Không cần nhắn thêm" mang tính ra lệnh; thêm tiêu chí tránh cách nói áp đặt. |
| 3 | H-042 | FAIL | PASS | Người | Phản hồi ngắn nhưng đủ ý; không bắt buộc phải xin lỗi trong mọi câu trả lời. |
| 4 | H-051 | FAIL | PASS | Người | Từ "refund" được quy định chấp nhận; thêm ví dụ từ mượn hợp lệ. |
| 5 | H-081 | FAIL | PASS | Judge | Ghi chú CSV xác định nhãn người sai; cần đối soát nhãn, không sửa CSV để tăng điểm. |

## Kết luận
- Loại `helpful`: confusion (TP=9, FP=0, FN=21, TN=70), recall=0.300, κ=0.375; bỏ sót 21/30 trường hợp FAIL. `tone_ok` có TP=24, FP=4, FN=6, TN=66 và vượt cả ba floors; chỉ dùng để hỗ trợ đánh giá giọng điệu. FAIL là lớp dương.
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật. H-081 cho thấy ngay cả nhãn người cũng có thể sai; số liệu hiện tại vẫn tính theo CSV gốc để bảo đảm tái lập.
