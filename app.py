import streamlit as st
from google import genai
from google.genai import types
import base64
import os
from pdf2image import convert_from_path
from PIL import Image
import img2pdf
import io
import tempfile
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="PDF Text Optimizer",
    page_icon="📄",
    layout="wide"
)

def convert_pdf_to_images(pdf_path, dpi=300):
    """Convert PDF to high-resolution images"""
    try:
        st.write(f"開始轉換 PDF，DPI={dpi}")
        images = convert_from_path(pdf_path, dpi=dpi)
        st.write(f"成功轉換 {len(images)} 頁")
        return images
    except Exception as e:
        st.error(f"Error converting PDF to images: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode()

def optimize_image_with_gemini(image, api_key, aspect_ratio="16:9"):
    """Use Gemini API to optimize text in image"""
    try:
        st.write(f"  → 初始化 Gemini 客戶端...")
        client = genai.Client(
            vertexai=True,
            api_key=api_key,
        )

        # Convert image to base64
        st.write(f"  → 轉換圖片格式...")
        img_base64 = image_to_base64(image)

        model = "gemini-3-pro-image-preview"
        st.write(f"  → 使用模型: {model}")

        # Create the content with the image and prompt
        prompt_text = "請優化這張圖片中的文字，使其更清晰、更易讀。保持原有的版面配置，但提升文字的品質、對比度和清晰度。請輸出優化後的圖片。"

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=prompt_text),
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/png",
                            data=base64.b64decode(img_base64)
                        )
                    )
                ]
            )
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            max_output_tokens=32768,
            response_modalities=["IMAGE"],
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )
            ],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size="2K"
            ),
        )

        # Generate optimized image
        st.write(f"  → 呼叫 Gemini API 進行優化...")
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

        st.write(f"  → 收到 API 回應，解析結果...")

        # Extract the generated image from response
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Get the image data
                        image_data = part.inline_data.data
                        # Convert to PIL Image
                        optimized_image = Image.open(io.BytesIO(image_data))
                        st.write(f"  → ✅ 成功生成優化圖片")
                        return optimized_image

        # If no image in response, return original
        st.warning(f"  → ⚠️ API 未返回優化圖片，使用原圖")
        st.write(f"  → 回應詳情: {response}")
        return image

    except Exception as e:
        st.error(f"  → ❌ 優化失敗: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return image

def images_to_pdf(images, output_path):
    """Convert list of PIL Images to PDF"""
    try:
        # Convert PIL images to bytes
        image_bytes_list = []
        for img in images:
            img_byte_arr = io.BytesIO()
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(img_byte_arr, format='PNG')
            image_bytes_list.append(img_byte_arr.getvalue())

        # Create PDF from images
        pdf_bytes = img2pdf.convert(image_bytes_list)

        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)

        return True
    except Exception as e:
        st.error(f"Error converting images to PDF: {str(e)}")
        return False

def main():
    st.title("📄 PDF 文字優化工具")
    st.markdown("### 使用 Gemini AI 優化 PDF 中的文字")

    # Sidebar for API key
    with st.sidebar:
        st.header("設定")
        api_key = st.text_input(
            "Google Cloud API Key",
            type="password",
            value=os.environ.get("GOOGLE_CLOUD_API_KEY", ""),
            help="輸入您的 Google Cloud API Key"
        )

        dpi = st.slider(
            "圖片解析度 (DPI)",
            min_value=150,
            max_value=600,
            value=300,
            step=50,
            help="更高的 DPI 會產生更清晰的圖片，但處理時間會更長"
        )

        aspect_ratio = st.selectbox(
            "輸出比例",
            options=["16:9", "4:3", "3:4", "9:16", "1:1"],
            index=0,
            help="選擇輸出圖片的長寬比例。16:9 適合投影片，3:4 適合文件"
        )

        st.markdown("---")
        st.markdown("#### 使用說明")
        st.markdown("""
        1. 輸入 API Key
        2. 上傳 PDF 檔案
        3. 點擊「開始處理」
        4. 等待處理完成
        5. 下載優化後的 PDF
        """)

    # File uploader
    uploaded_file = st.file_uploader(
        "選擇 PDF 檔案",
        type=['pdf'],
        help="上傳要優化的 PDF 檔案"
    )

    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ 已上傳檔案: {uploaded_file.name}")

        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            preview_button = st.button("👁️ 預覽第一頁", width='stretch', help="快速預覽優化效果，節省時間和成本")
        with col2:
            process_button = st.button("🚀 處理全部", type="primary", width='stretch', help="處理 PDF 的所有頁面")

        if preview_button or process_button:
            preview_mode = preview_button  # 判斷是否為預覽模式
            if not api_key:
                st.error("⚠️ 請先在側邊欄輸入 Google Cloud API Key")
                return

            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)

                # Save uploaded PDF
                pdf_path = temp_dir_path / "input.pdf"
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                # Step 1: Convert PDF to images
                st.markdown("---")
                if preview_mode:
                    st.info("🔍 預覽模式：只處理第一頁")
                st.subheader("📑 步驟 1: 將 PDF 轉換為圖片")
                status_1 = st.status("處理中...", expanded=True)

                with status_1:
                    st.write("正在轉換 PDF...")
                    images = convert_pdf_to_images(str(pdf_path), dpi=dpi)

                    if images is None:
                        st.error("PDF 轉換失敗")
                        return

                    total_pages = len(images)

                    # 預覽模式只處理第一頁
                    if preview_mode:
                        images = [images[0]]
                        st.success(f"✅ 成功轉換第 1 頁（PDF 共有 {total_pages} 頁）")
                    else:
                        st.success(f"✅ 成功轉換 {len(images)} 頁")

                    # Show preview of first page
                    st.write("第一頁預覽:")
                    st.image(images[0], width=300)

                status_1.update(label="✅ PDF 轉換完成", state="complete")

                # Step 2: Optimize images with Gemini
                st.subheader("🤖 步驟 2: 使用 Gemini AI 優化圖片")
                status_2 = st.status("處理中...", expanded=True)

                optimized_images = []

                with status_2:
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    status_log = st.empty()

                    success_count = 0
                    fail_count = 0

                    for idx, img in enumerate(images):
                        progress_text.text(f"正在處理第 {idx + 1}/{len(images)} 頁...")

                        st.write(f"📄 處理頁面 {idx + 1}/{len(images)}...")

                        # Optimize image
                        optimized_img = optimize_image_with_gemini(img, api_key, aspect_ratio)

                        # Check if optimization actually happened
                        if optimized_img is img:
                            st.warning(f"⚠️ 第 {idx + 1} 頁優化失敗，使用原圖")
                            fail_count += 1
                        else:
                            st.success(f"✅ 第 {idx + 1} 頁優化成功")
                            success_count += 1

                        optimized_images.append(optimized_img)

                        # Update progress
                        progress = (idx + 1) / len(images)
                        progress_bar.progress(progress)

                    progress_text.text(f"✅ 已完成 {len(optimized_images)} 頁的處理")
                    status_log.info(f"成功優化: {success_count} 頁 | 失敗: {fail_count} 頁")

                    # Show comparison
                    st.write("優化前後對比 (第一頁):")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("原始圖片")
                        st.image(images[0], width='stretch')
                    with col2:
                        st.write("優化後")
                        st.image(optimized_images[0], width='stretch')

                status_2.update(label="✅ 圖片優化完成", state="complete")

                # Step 3: Convert images back to PDF (skip in preview mode)
                if not preview_mode:
                    st.subheader("📄 步驟 3: 重組為 PDF")
                    status_3 = st.status("處理中...", expanded=True)

                    with status_3:
                        st.write("正在生成 PDF...")

                        output_pdf_path = temp_dir_path / "optimized.pdf"
                        success = images_to_pdf(optimized_images, str(output_pdf_path))

                        if not success:
                            st.error("PDF 生成失敗")
                            return

                        st.success("✅ PDF 生成成功")

                    status_3.update(label="✅ PDF 重組完成", state="complete")

                    # Step 4: Provide download button
                    st.markdown("---")
                    st.subheader("📥 下載優化後的 PDF")

                    with open(output_pdf_path, "rb") as f:
                        pdf_bytes = f.read()

                    st.download_button(
                        label="⬇️ 下載優化後的 PDF",
                        data=pdf_bytes,
                        file_name=f"optimized_{uploaded_file.name}",
                        mime="application/pdf",
                        type="primary",
                        width='stretch'
                    )

                    st.success("🎉 所有處理已完成！")
                else:
                    # Preview mode: show suggestion to process all
                    st.markdown("---")
                    st.success("✅ 預覽完成！")
                    st.info(f"💡 如果效果滿意，可以點擊「處理全部」按鈕來處理完整的 {total_pages} 頁 PDF")

                    # Provide download button for single optimized image
                    st.subheader("📥 下載優化後的圖片")

                    # Convert optimized image to bytes
                    img_byte_arr = io.BytesIO()
                    optimized_images[0].save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()

                    st.download_button(
                        label="⬇️ 下載優化後的第一頁 (PNG)",
                        data=img_bytes,
                        file_name=f"preview_page1_{uploaded_file.name.replace('.pdf', '.png')}",
                        mime="image/png",
                        width='stretch'
                    )

if __name__ == "__main__":
    main()
