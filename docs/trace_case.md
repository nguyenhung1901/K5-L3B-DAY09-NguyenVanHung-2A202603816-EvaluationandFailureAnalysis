# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi bạn 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`. Chưa có run ID từ `reports/eval_seeded_regression.json` (sẽ bổ sung sau khi chạy eval M3/M4). |
| Triệu chứng | Lab 8 grader FAIL (`status resolved != denied`); reply báo hoàn 20.000 VND, ledger ghi 20.000 VND/1 refund, trong khi nhãn yêu cầu `denied`, 0 VND/0 refund. |
| Bước sai đầu tiên | Event 3, `model_override`: `{"delay_days": 5}`. |
| Vì sao là bước *đầu tiên* | Event 1 `handoff` chỉ giao nhiệm vụ; event 2 `investigator` đọc `delay_days=2` của O-202 từ DB. Sai lệch xuất hiện tại event 3, trước `quote` ở event 4. |
| Failure mode | FM-03 — `ticket_trust`. |
| Đối chứng | `fixed C-002@11`: không có `model_override`; event 3 `quote` = 0 VND, event 4 `reply` từ chối; ledger 0 VND, trạng thái `denied`, Lab 8 grader PASS. |
| Regression test | `tests/test_lab9_evalset.py::test_fm03_c002_trace_regression`: assert `seeded_regression` tạo `model_override` và refund 20.000 VND, `fixed` không override và refund 0 VND. Đã thêm vào bản patch; **chưa có log pytest trên máy người làm để xác nhận PASS**. |
| Chưa chắc chắn | Một trial/seed không chứng minh mọi seed hoặc LLM thật đều tương tự; grader chỉ dựa event `model_override` có thể bỏ sót `quiet_override`. Run ID báo cáo chưa có. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
