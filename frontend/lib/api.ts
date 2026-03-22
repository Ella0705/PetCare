import { FinalPetHealthReport } from "./types";

/**
 * - 未设置 NEXT_PUBLIC_API_BASE：走同源 /api/report（Next 服务端代理到 FastAPI，推荐本地开发）
 * - 已设置：浏览器直连该地址（需后端 CORS 允许你的前端来源）
 */
function getReportUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "");
  if (base) {
    return `${base}/api/report`;
  }
  if (typeof window !== "undefined") {
    return `${window.location.origin}/api/report`;
  }
  return "/api/report";
}

export async function createReport(formData: FormData): Promise<FinalPetHealthReport> {
  let res: Response;
  try {
    res = await fetch(getReportUrl(), {
      method: "POST",
      body: formData
    });
  } catch (e) {
    const hint =
      e instanceof Error ? e.message : String(e);
    throw new Error(
      `网络请求失败（Failed to fetch）。请确认：1) 后端已在 backend 目录运行 uvicorn（端口 8000）；2) 若使用直连 API，请检查 NEXT_PUBLIC_API_BASE 与 CORS。详情: ${hint}`
    );
  }

  if (!res.ok) {
    let msg = `API 错误: HTTP ${res.status}`;
    try {
      const ct = res.headers.get("Content-Type") || "";
      if (ct.includes("application/json")) {
        const j = (await res.json()) as { detail?: string };
        if (typeof j?.detail === "string") {
          msg = j.detail;
        }
      }
    } catch {
      /* ignore */
    }
    throw new Error(msg);
  }

  return res.json() as Promise<FinalPetHealthReport>;
}
