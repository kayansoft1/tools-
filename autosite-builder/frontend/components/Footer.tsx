import type { SiteData } from "../pages/s/[slug]";

interface Props {
  data: SiteData;
}

export default function Footer({ data }: Props) {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white px-6 py-10 text-center">
      <p className="text-lg font-bold mb-2">{data.name}</p>
      <p className="text-gray-400 text-sm">
        © {year} {data.name}. جميع الحقوق محفوظة.
      </p>
    </footer>
  );
}
