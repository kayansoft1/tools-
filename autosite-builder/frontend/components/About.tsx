interface Props {
  content: string;
}

export default function About({ content }: Props) {
  if (!content) {
    return null;
  }

  return (
    <section className="px-6 py-16 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">من نحن</h2>
      <p className="text-gray-700 leading-loose text-lg whitespace-pre-line text-center">
        {content}
      </p>
    </section>
  );
}
