# widgets.py

from django import forms
from django.utils.safestring import mark_safe

class S3UploadWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)
        safe_name = name.replace("-", "_")

        return mark_safe(f'''
            {input_html}
            <input type="file" id="file_{safe_name}" />
            <button type="button" onclick="upload_{safe_name}()">Upload to S3</button>
            <script>
                async function upload_{safe_name}() {{
                    const fileInput = document.getElementById("file_{safe_name}");
                    if (!fileInput.files.length) {{
                        alert("No file selected");
                        return;
                    }}

                    const file = fileInput.files[0];
                    const res = await fetch("/api/upload-url/?content_type=" + encodeURIComponent(file.type));
                    const data = await res.json();

                    const formData = new FormData();
                    for (const [key, value] of Object.entries(data.fields)) {{
                        formData.append(key, value);
                    }}
                    formData.append("file", file);

                    const upload = await fetch(data.url, {{
                        method: "POST",
                        body: formData,
                    }});

                    if (upload.ok) {{
                        document.querySelector("input[name='{name}']").value = data.final_url;
                        alert("Upload successful");
                    }} else {{
                        alert("Upload failed");
                    }}
                }}
            </script>
        ''')

