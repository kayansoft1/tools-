import type { SiteData } from "../pages/s/[slug]";

interface Props {
  data: SiteData;
}

export default function Contact({ data }: Props) {
  const hasLocation =
    data.latitude !== null && data.latitude !== undefined &&
    data.longitude !== null && data.longitude !== undefined;

  return (
    <section className="bg-gray-50 px-6 py-16">
      <h2 className="text-3xl font-bold text-center mb-10 text-gray-800">تواصل معنا</h2>
      <div className="max-w-4xl mx-auto space-y-4 text-center">
        {data.phone && (
          <p className="text-lg text-gray-700">
            <span className="font-bold">الهاتف: </span>
            <a href={`tel:${data.phone}`} className="text-primary hover:underline">
              {data.phone}
            </a>
          </p>
        )}
        {data.address && (
          <p className="text-lg text-gray-700">
            <span className="font-bold">العنوان: </span>
            {data.address}
          </p>
        )}
        {hasLocation && (
          <div className="mt-8 rounded-xl overflow-hidden shadow">
            <iframe
              title="موقعنا على الخريطة"
              width="100%"
              height="360"
              loading="lazy"
              src={`https://maps.google.com/maps?q=${data.latitude},${data.longitude}&z=15&output=embed`}
            />
          </div>
        )}
      </div>
    </section>
  );
}
