import fs from "fs";
import path from "path";
import type { GetStaticPaths, GetStaticProps } from "next";
import Head from "next/head";
import Hero from "../../components/Hero";
import Services from "../../components/Services";
import About from "../../components/About";
import Contact from "../../components/Contact";
import Footer from "../../components/Footer";
import WhatsAppButton from "../../components/WhatsAppButton";

export interface SiteData {
  place_id: string;
  name: string;
  category: string;
  city: string;
  phone: string | null;
  whatsapp: string | null;
  address: string;
  latitude: number | null;
  longitude: number | null;
  rating: number;
  reviews_count: number;
  content: {
    short_description: string;
    long_description: string;
    services: { name: string; description: string; icon: string }[];
    faq: { q: string; a: string }[];
    seo_title: string;
    seo_description: string;
  };
  social: {
    instagram_url: string | null;
    tiktok_url: string | null;
    snapchat_url: string | null;
    facebook_url: string | null;
  };
}

interface Props {
  data: SiteData;
}

const DATA_DIR = path.join(process.cwd(), "data");

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const files = fs.readdirSync(DATA_DIR);
    const paths = files
      .filter((file) => file.endsWith(".json"))
      .map((file) => ({ params: { slug: file.replace(/\.json$/, "") } }));
    return { paths, fallback: "blocking" };
  } catch {
    return { paths: [], fallback: "blocking" };
  }
};

export const getStaticProps: GetStaticProps<Props> = async (context) => {
  const slug = context.params?.slug as string;
  const filePath = path.join(DATA_DIR, `${slug}.json`);
  try {
    const raw = fs.readFileSync(filePath, "utf-8");
    const data: SiteData = JSON.parse(raw);
    return { props: { data }, revalidate: 60 };
  } catch {
    return { notFound: true };
  }
};

export default function SitePage({ data }: Props) {
  const { content } = data;
  const title = content.seo_title || data.name;
  const description = content.seo_description || content.short_description;
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    name: data.name,
    description: content.short_description,
    address: {
      "@type": "PostalAddress",
      streetAddress: data.address,
      addressLocality: data.city,
    },
    telephone: data.phone || undefined,
    aggregateRating:
      data.rating > 0
        ? {
            "@type": "AggregateRating",
            ratingValue: data.rating,
            reviewCount: data.reviews_count,
          }
        : undefined,
    geo:
      data.latitude != null && data.longitude != null
        ? {
            "@type": "GeoCoordinates",
            latitude: data.latitude,
            longitude: data.longitude,
          }
        : undefined,
  };
  return (
    <>
      <Head>
        <html lang="ar" dir="rtl" />
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta property="og:type" content="website" />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:locale" content="ar_SA" />
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <link
          rel="canonical"
          href={`https://${process.env.NEXT_PUBLIC_SITE_DOMAIN || "localhost"}/s/${data.place_id}`}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </Head>
      <main dir="rtl" className="font-arabic">
        <Hero data={data} />
        <Services services={content.services} />
        <About content={content.long_description} />
        <Contact data={data} />
        <Footer data={data} />
        <WhatsAppButton phone={data.whatsapp || data.phone || ""} />
      </main>
    </>
  );
}
