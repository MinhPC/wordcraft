# Review nâng cấp giao diện WordCraft theo Microsoft Word

Ngày review: 2026-10-14. Phạm vi: bố cục, khả năng tìm lệnh và tương tác của giao diện Rust/egui; đây là đề xuất nâng cấp, chưa phải tính năng đã triển khai.

## Kết luận

WordCraft đã có cấu trúc quen thuộc với người dùng Word: Quick Access Toolbar, ribbon theo nhóm, contextual tabs, Styles gallery, Navigation pane, Backstage, rulers và status bar. Nâng cấp có giá trị nhất là giữ giao diện sử dụng được khi cửa sổ hẹp hoặc tăng interface size, hiển thị rõ trạng thái tài liệu và hoàn thiện khả năng truy cập của controls tự vẽ.

Không lấy tỷ lệ command catalog làm tỷ lệ hoàn thiện giao diện. Một lệnh tồn tại vẫn có thể khó tìm, bị che hoặc thiếu thông tin cho screen reader.

## Bằng chứng và giới hạn

- Đọc `crates/ui-egui/src/{chrome,ribbon,widgets,panes,backstage,dialogs,theme,a11y}.rs`, `docs/ui-parity.md` và roadmap hiện có.
- Quan sát ảnh trong repo: `docs/images/hero.png`, `docs/images/backstage.png`. Những ảnh này là minh họa đã lưu, không xác nhận bản chạy hiện tại.
- Biên dịch offline thành công và chạy `ui_shot` với sample ở 1440×900 và 960×720, render 2×. Đã đọc cả hai PNG: [wide](../target/ui-review/wide.png), [narrow](../target/ui-review/narrow.png). Ảnh ở `target/` là artifact local, không commit. Headless example đặt `integrated_titlebar = true` kể cả trên Windows; đây là bằng chứng về layout egui, chưa phải toàn bộ chrome của cửa sổ Windows thật.
- Ảnh narrow xác nhận tiêu đề biến mất và Comments/Editing đè lên các tab cuối. Ảnh wide hiển thị đầy đủ tiêu đề; nội dung ribbon vẫn phải cuộn ngang để tới các nhóm cuối.
- Tài liệu parity của repo lấy Word for Mac 16.113.4 làm chuẩn. Các hành vi Navigation được dẫn dưới đây lấy từ tài liệu Word for Windows; cần đối chiếu riêng từng nền tảng.
- Chưa có bản Word chạy được quan sát trực tiếp trong review này. Không kết luận pixel parity, không xác nhận NVDA/VoiceOver chỉ từ mã nguồn.
- `../../craftrules/AGENTS.md` không có tại vị trí được chỉ dẫn; URL GitHub tương ứng không truy cập được. Review dựa trên các quy tắc clean-room đã có trong AGENTS.md của WordCraft.

## Findings theo thứ tự ưu tiên

### P1 — Tên và trạng thái tài liệu biến mất khi thiếu chỗ

`chrome.rs:317–346` chỉ vẽ toàn bộ tiêu đề nếu nó vừa khoảng trống giữa QAT và controls bên phải. Không có nhánh rút gọn. Search có chiều rộng cố định 260 pt; Discord chiếm thêm 84 pt. Tên dài, QAT tùy biến hoặc cửa sổ hẹp làm mất cả tên tài liệu và trạng thái Edited/Saved/Not saved.

Đã tái hiện với sample và QAT mặc định ở 960×720; không cần tên dài hoặc QAT tùy biến để gặp lỗi.

Đề xuất: luôn giữ một vùng tối thiểu cho tên và trạng thái; ellipsis tên theo chiều rộng thực, tooltip hiện tên đầy đủ; thu Search về nút khi thiếu chỗ; chuyển community link vào Help/menu phụ. Trạng thái lưu cần có vị trí riêng, không phụ thuộc việc tên có vừa hay không.

Nghiệm thu: tại 960 pt, với tên dài và QAT 10 nút, vẫn đọc được trạng thái lưu và phần nhận diện tài liệu; Search vẫn truy cập được bằng chuột và phím tắt.

### P1 — Hàng tab chưa xử lý tràn

`ribbon.rs:188–268` đặt tất cả tabs và Comments/Editing/Share trên cùng một hàng ngang. Contextual tabs và custom tabs tăng chiều rộng; chưa có overflow menu hoặc vùng cuộn cho hàng này. Phần nội dung ribbon đã có horizontal scroll và chevrons (`ribbon.rs:288–349`), nhưng cơ chế đó không bảo vệ hàng tab.

Đã tái hiện ở 960×720: các controls bên phải vẽ đè lên vùng Developer/Zotero/Help. Chưa kiểm tra click vào vùng chồng để kết luận control nào nhận sự kiện.

Đề xuất: tính ngân sách chiều rộng riêng cho tabs và actions; dùng overflow menu hoặc cuộn tabs có chỉ báo; luôn giữ tab đang chọn nhìn thấy; thu actions về icons có nhãn truy cập ở cửa sổ hẹp. Duy trì thứ tự tùy biến và keytips.

Nghiệm thu: Home, File và tab ngữ cảnh đang chọn luôn truy cập được ở 960 pt, interface size 150%, có custom tabs và Table Design/Table Layout; không chồng vùng hit-test.

### P1 — Thông tin accessibility của controls tự vẽ chưa đồng đều

`widgets.rs:189–209` có `widget_info` cho small buttons; các đường vẽ big buttons (`widgets.rs:145–186`), QAT (`chrome.rs:11–26`), AutoSave và Search chưa có thông tin tương đương tại nơi tạo control. Nhãn vẽ bằng painter và tooltip không đủ chứng minh tên, role hoặc trạng thái trong AccessKit tree. Các tab và view buttons đã có metadata: nên mở rộng theo cùng hướng.

Đề xuất: chuẩn hóa helper cho button/toggle/split button với tên, role, enabled và checked state. Lý do disabled dùng kết quả command registry. Kiểm tra focus ring và kích hoạt bàn phím phù hợp với quy tắc toolbar của dự án.

Nghiệm thu: kiểm tra AccessKit output cho Save, Paste, AutoSave, Search và Share; thử một luồng mở–định dạng–lưu bằng NVDA trên Windows, và VoiceOver khi có môi trường macOS.

### P2 — Navigation › Pages chỉ có tên trang

`panes.rs:147–155` dựng danh sách “Page n”, chưa có thumbnail. Heading hiện tại được suy ra từ caret (`panes.rs:178–196`), nên cần kiểm tra riêng khi người dùng chỉ cuộn mà không di chuyển caret. Word for Windows mô tả Pages bằng thumbnail và cập nhật mục đang xem khi cuộn.

Đề xuất: thumbnail từ page renderer hiện có, cache theo revision, chỉ render các mục nhìn thấy; xác định trang/heading đang xem bằng viewport. Giữ caret khi chỉ cuộn.

Nghiệm thu: tài liệu nhiều trang có thể nhận diện trang bằng hình; cuộn cập nhật mục đang xem; cache có giới hạn, không rasterize toàn bộ tài liệu mỗi frame.

### P2 — Search có hình thức ô nhập nhưng mở dialog, kết quả chưa phản ánh enabled state

`chrome.rs:282–313` vẽ Search bằng `Sense::click`, sau đó mở `Dialog::Commands`. `dialogs.rs:2236–2265` trả tối đa 14 kết quả; Enter chọn kết quả đầu, và các nút kết quả chưa kiểm tra `(c.enabled)(&app.session)` trước khi trình bày.

Đề xuất: giữ command search hiện có, bổ sung chọn kết quả bằng Up/Down/Enter, hiển thị disabled và lý do; ưu tiên kết quả phù hợp ngữ cảnh. Cân nhắc popup neo dưới Search để giảm bước chuyển ngữ cảnh; Find trong tài liệu tiếp tục mở Navigation.

Nghiệm thu: tìm lệnh không áp dụng được không hiển thị như lệnh dùng được; Enter chạy mục đang chọn; Esc trả focus về tài liệu; gọi `tools.search` có query từ agent vẫn trả dữ liệu như hiện tại.

### P2 — Backstage Home chưa thích ứng như New

`backstage.rs:231–237` dùng một hàng `horizontal` cho templates; New đã dùng `horizontal_wrapped` (`backstage.rs:263`). Navigation rộng cố định 200 pt. Cửa sổ hẹp và interface size lớn cần kiểm chứng nguy cơ template bị cắt.

Đề xuất: gallery Home tự xuống hàng hoặc giảm số tiles với liên kết More templates; ưu tiên Blank document và Recent. Giữ navigation ổn định, đồng thời bảo đảm phần nội dung còn đủ rộng.

Nghiệm thu: Home và New tại 960 pt/150% không cắt tile hay caption; Blank document, Open và Recent tiếp cận được bằng bàn phím.

### P3 — Hoàn thiện ribbon và thao tác trực tiếp trên trang

Ribbon content hiện cuộn ngang toàn bộ khi thiếu chỗ. Sau khi sửa P1, bổ sung co nhóm theo mức độ quan trọng: giữ Clipboard/Font/Paragraph dùng nhanh; thu Styles gallery và nhóm ít dùng thành menu. Chế độ ribbon gọn có thể là lựa chọn sản phẩm; tài liệu single-line ribbon được dẫn dưới đây áp dụng cho Word web, không mặc định là chuẩn Word desktop.

Crop handles và alignment guides vẫn được ghi là thiếu trong `docs/ui-parity.md`. Đây là nâng cấp hữu ích cho bố cục ảnh, nhưng nên làm sau khi các controls hiện có sử dụng ổn định ở nhiều kích thước.

## Trình tự triển khai

1. Sửa title/status fallback và tab overflow; kiểm chứng kích thước cửa sổ và interface size.
2. Chuẩn hóa accessibility cho custom controls; sửa enabled state và chọn kết quả Search.
3. Bổ sung Navigation thumbnails, viewport tracking và Backstage Home thích ứng.
4. Co nhóm ribbon; sau đó làm crop handles và guides.

Mỗi bước giữ UI ở L6; thao tác tài liệu đi qua command registry. Dùng `theme::Tokens`, icons nguyên bản trong `icons.rs`, không sao chép asset Microsoft. Không thay đổi tỷ lệ parity/readiness chỉ vì báo cáo này được thêm.

## Ma trận kiểm chứng khi triển khai

- Headless `ui_shot`: 960×720, 1280×800, 1440×900; light/dark; interface size Auto/100%/150%/200%.
- Trạng thái: tài liệu chưa lưu/đã lưu/đã sửa; tên dài; QAT 10 nút; custom tabs; chọn bảng/ảnh; Navigation và Comments cùng mở.
- Interaction tests: các tab trong overflow, title fallback, Search chọn bằng phím, disabled command, focus trở về canvas; AccessKit metadata của controls đã sửa.
- Không dùng screenshot golden test phụ thuộc font hệ thống để chứng minh hành vi. Kiểm tra vùng controls và kết quả command bằng egui harness, rồi đọc screenshot để đánh giá bố cục.
- Trước commit triển khai: `cargo xtask ci` gồm fmt, clippy, tests, assets, layers và wasm. Khi tính năng thực sự hoàn thành, cập nhật gaps, parity và progress log.

## Tài liệu đối chiếu công khai

- [Microsoft: Customize the ribbon in Word](https://support.microsoft.com/en-us/word/customize-the-ribbon-in-word).
- [Microsoft: Use the Navigation pane in Word](https://support.microsoft.com/en-us/word/use-the-navigation-pane-in-word) — áp dụng Word Windows, có lưu ý khác biệt Mac/web.
- [Microsoft: Use a screen reader to explore and navigate Word](https://support.microsoft.com/en-US/accessibility/word/use-a-screen-reader-to-explore-and-navigate-word).
- [Microsoft: Using the single line ribbon in Word for the web](https://support.microsoft.com/en-gb/word/using-the-simplified-ribbon-in-word-for-the-web).
