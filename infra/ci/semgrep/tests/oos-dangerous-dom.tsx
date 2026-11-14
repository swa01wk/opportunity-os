/* eslint-disable @typescript-eslint/no-unused-vars */
// ruleid: oos.tsx.dangerous-inner-html
export const bad = <div dangerouslySetInnerHTML={{ __html: "x" }} />;

// ok: oos.tsx.dangerous-inner-html
export const good = <div>text</div>;