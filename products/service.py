import asyncio
from googletrans import Translator

async def async_translate(text: str, dest: str) -> str:
    translator = Translator()
    result = await translator.translate(text, dest=dest)
    return result.text

def translate_product_name(product):
    """
    Auto-translate Product.name_<lang> fields based on whichever one the user provided.
    - If user supplied name_en, translate to ru & uz.
    - Else if name_ru supplied, translate to en & uz.
    - Else if name_uz supplied, translate to en & ru.
    - Skip if none provided.
    """
    # Map of our fields
    langs = ['en', 'ru', 'uz']

    # 1️⃣ Find the first language the user actually entered
    source_lang = None
    for lang in langs:
        val = getattr(product, f'name_{lang}', None)
        if val and val.strip():
            source_lang = lang
            source_text = val.strip()
            break

    # Nothing to translate
    if not source_lang:
        return

    # 2️⃣ Translate into any missing languages
    updated_fields = []
    for target_lang in langs:
        if target_lang == source_lang:
            continue
        target_field = f'name_{target_lang}'
        current = getattr(product, target_field, None) or ''
        if not current.strip():
            try:
                translated = asyncio.run(
                    async_translate(source_text, dest=target_lang)
                )
                setattr(product, target_field, translated)
                updated_fields.append(target_field)
            except Exception as e:
                print(f"[Translation Error] could not fill {target_field}: {e}")

    # 3️⃣ Persist only the newly filled fields
    if updated_fields:
        product.save(update_fields=updated_fields)
