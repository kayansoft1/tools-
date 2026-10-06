import type { SiteData } from "../pages/s/[slug]";

interface Props {
  data: SiteData;
}

export default function Hero({ data }: Props) {
  const phone = (data.phone || "").replace(/[^\d+]/g, "");
  const whatsapp = (data.whatsapp || data.phone || "").replace(/[^\d]/g, "");

  return (
    <section className="bg-gradient-to-br from-primary to-blue-900 text-white px-6 py-20 text-center">
      <h1 className="text-4xl md:text-6xl font-extrabold mb-4">{data.name}</h1>
      <p className="text-lg md:text-xl max-w-3xl mx-auto leading-relaxed mb-8">
        {data.content.short_description}
      </p>
      <div className="flex flex-wrap gap-4 justify-center">
        {phone && (
          <a
            href={`tel:${phone}`}
            className="bg-white text-primary font-bold px-6 py-3 rounded-full shadow hover:bg-gray-100 transition"
          >
            اتصل الآن
          </a>
        )}
        {whatsapp && (
          <a
            href={`https://wa.me/${whatsapp}`}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-secondary text-white font-bold px-6 py-3 rounded-full shadow hover:opacity-90 transition"
          >
            واتساب
          </a>
        )}
      </div>
    </section>
  );
}
