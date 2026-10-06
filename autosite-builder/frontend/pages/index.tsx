import Head from "next/head";

export default function Home() {
  return (
    <>
      <Head>
        <title>AutoSite Builder</title>
        <meta
          name="description"
          content="نظام آلي لبناء مواقع إلكترونية للمنشآت المحلية بدون موقع."
        />
      </Head>
      <main
        dir="rtl"
        className="font-arabic min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-primary to-blue-900 text-white px-6 text-center"
      >
        <h1 className="text-4xl md:text-6xl font-extrabold mb-4">AutoSite Builder</h1>
        <p className="text-lg md:text-xl max-w-2xl leading-relaxed">
          نظام آلي يبحث عن المنشآت المحلية التي لا تمتلك موقعاً إلكترونياً، ويولّد
          لها مواقع عربية جاهزة تلقائياً.
        </p>
      </main>
    </>
  );
}
