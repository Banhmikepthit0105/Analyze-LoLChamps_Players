import re

def clean_the_response(generated_code):
    """
    Loại bỏ các ký hiệu markdown dùng để định dạng code (```python và ```).
    Trả về mã code thuần đã được làm sạch.
    """
    if generated_code.startswith('```python'):
        generated_code = generated_code[len('```python'):].strip()
    if generated_code.endswith('```'):
        generated_code = generated_code[:-len('```')].strip()
    return generated_code