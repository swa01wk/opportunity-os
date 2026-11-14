# ruleid: oos.tsx.dangerous-inner-html
_BAD_JSX = '<div dangerouslySetInnerHTML={{ __html: "x" }} />'

# ok: oos.tsx.dangerous-inner-html
_GOOD_JSX = "<div>text</div>"
