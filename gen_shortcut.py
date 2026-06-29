"""
iOS Shortcut (.shortcut) file generate kore.

Cholao:
    python gen_shortcut.py <domain> <DL_KEY> [--audio]

Jemon:
    python gen_shortcut.py save.hunterflow.cloud my-secret-key
    python gen_shortcut.py save.hunterflow.cloud my-secret-key --audio   # mp3 version

Output: Download.shortcut (ba Download-MP3.shortcut). iPhone e pathiye import koro.
(Settings > Shortcuts > "Allow Untrusted Shortcuts" ON lagte pare.)
"""
import sys
import plistlib

OBJ = "￼"  # object-replacement char = variable placeholder


def text_token(string, attachments=None):
    return {
        "WFSerializationType": "WFTextTokenString",
        "Value": {"string": string, "attachmentsByRange": attachments or {}},
    }


def form_item(key, value_token):
    return {
        "WFItemType": 0,
        "WFKey": text_token(key),
        "WFValue": value_token,
    }


def build(domain, key, audio=False):
    base_url = f"https://{domain}/dl"

    # Shortcut input (share sheet theke asha link) ke url field e boshai
    input_token = text_token(OBJ, {"{0, 1}": {"Type": "ExtensionInput"}})

    items = [
        form_item("url", input_token),
        form_item("key", text_token(key)),
    ]
    if audio:
        items.append(form_item("audio", text_token("1")))

    get_contents = {
        "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
        "WFWorkflowActionParameters": {
            "WFURL": base_url,
            "ShowHeaders": False,
            "WFHTTPMethod": "POST",
            "WFHTTPBodyType": "Form",
            "WFFormValues": {
                "WFSerializationType": "WFDictionaryFieldValue",
                "Value": {"WFDictionaryFieldValueItems": items},
            },
        },
    }

    save_file = {
        "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.save",
        "WFWorkflowActionParameters": {
            "WFAskWhereToSave": True,
        },
    }

    return {
        "WFWorkflowClientVersion": "2607.0.2",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 4271458815,
            "WFWorkflowIconGlyphNumber": 61440,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowTypes": ["ActionExtension"],
        "WFWorkflowHasShortcutInputVariables": True,
        "WFWorkflowInputContentItemClasses": [
            "WFArticleContentItem", "WFContentItem", "WFGenericFileContentItem",
            "WFImageContentItem", "WFAVAssetContentItem", "WFPDFContentItem",
            "WFRichTextContentItem", "WFSafariWebPageContentItem",
            "WFStringContentItem", "WFURLContentItem",
        ],
        "WFWorkflowActions": [get_contents, save_file],
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    audio = "--audio" in sys.argv
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    domain, key = args[0], args[1]
    plist = build(domain, key, audio=audio)
    out = "Download-MP3.shortcut" if audio else "Download.shortcut"
    with open(out, "wb") as f:
        plistlib.dump(plist, f, fmt=plistlib.FMT_BINARY)
    # validate round-trip
    with open(out, "rb") as f:
        plistlib.load(f)
    print(f"OK -> {out}  (domain={domain}, audio={audio})")


if __name__ == "__main__":
    main()
