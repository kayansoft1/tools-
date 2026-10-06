import fs from "fs";
import path from "path";
import type { GetServerSideProps } from "next";

const DATA_DIR = path.join(process.cwd(), "data");

function buildSitemap(): string {
  const domain = process.env.NEXT_PUBLIC_SITE_DOMAIN || "localhost";
  const base = `https://${domain}`;
  let slugs: string[] = [];
  try {
    slugs = fs
      .readdirSync(DATA_DIR)
      .filter((file) => file.endsWith(".json"))
      .map((file) => file.replace(/\.json$/, ""));
  } catch {
    slugs = [];
  }
  const urls = [
    `<url><loc>${base}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>`,
    ...slugs.map(
      (slug) =>
        `<url><loc>${base}/s/${slug}</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>`
    ),
  ].join("");
  return `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}</urlset>`;
}

export const getServerSideProps: GetServerSideProps = async ({ res }) => {
  res.setHeader("Content-Type", "application/xml");
  res.write(buildSitemap());
  res.end();
  return { props: {} };
};

export default function Sitemap() {
  return null;
}
