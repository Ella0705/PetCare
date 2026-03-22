import { NextRequest, NextResponse } from "next/server";

/**
 * 浏览器只请求同源 /api/report，由 Next 服务端转发到 FastAPI，
 * 避免 localhost:3000 → 127.0.0.1:8000 的跨域/CORS 问题。
 */
const BACKEND = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export async function POST(request: NextRequest) {
  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return NextResponse.json({ detail: "Invalid form data" }, { status: 400 });
  }

  try {
    const res = await fetch(`${BACKEND}/api/report`, {
      method: "POST",
      body: formData
    });

    const text = await res.text();
    const contentType = res.headers.get("Content-Type") || "application/json";

    return new NextResponse(text, {
      status: res.status,
      headers: { "Content-Type": contentType }
    });
  } catch (e) {
    const message =
      e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json(
      {
        detail: `无法连接后端 (${BACKEND})。请先在 backend 目录启动: uvicorn app.main:app --reload --port 8000。${message}`
      },
      { status: 502 }
    );
  }
}
