/**
 * ============================================================
 *  pdfmake-fonts.js — NotoSansSC 中文字体加载器（本地版）
 *
 *  字体文件位于 public/fonts/NotoSansSC-Regular.otf
 *  Vite 将 public/ 目录作为静态资源根路径提供服务，
 *  build 时自动复制到 dist/ 根目录。
 *
 *  下载地址：
 *    https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/SubsetOTF/SC/NotoSansSC-Regular.otf
 *
 *  使用方式：
 *    1. 下载上述文件并放入 public/fonts/NotoSansSC-Regular.otf
 *    2. 本模块在首次调用时 fetch('/fonts/NotoSansSC-Regular.otf')
 *       转为 Base64 并注册到 pdfMake.vfs / pdfMake.fonts
 * ============================================================
 */

// Vite 中 public/ 目录下的文件可通过绝对路径访问
// dev: http://localhost:5173/fonts/NotoSansSC-Regular.otf
// build: 同样 /fonts/NotoSansSC-Regular.otf（dist 根目录）
const FONT_URL = '/fonts/NotoSansSC-Regular.otf'

const FONT_NAME = 'NotoSansSC'
const VFS_KEY = 'NotoSansSC-Regular.otf'

/** @type {string | null} */
let cachedBase64 = null

/** @type {Promise<string> | null} */
let pendingLoad = null

/**
 * ArrayBuffer → Base64（浏览器兼容）
 */
function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}

/**
 * fetch 本地字体文件 → 转为 Base64
 * 结果缓存在内存中，多次调用只请求一次
 */
export async function getFontBase64() {
  if (cachedBase64) return cachedBase64

  const res = await fetch(FONT_URL)

  console.log('status=', res.status)
  console.log('content-type=', res.headers.get('content-type'))

  const text = await res.clone().text()

  console.log('first200=')
  console.log(text.substring(0, 200))

  const buf = await res.arrayBuffer()

  console.log('buffer size=', buf.byteLength)

  cachedBase64 = arrayBufferToBase64(buf)

  console.log('base64 length=', cachedBase64.length)

  return cachedBase64
}