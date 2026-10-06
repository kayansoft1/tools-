interface Service {
  name: string;
  description: string;
  icon: string;
}

interface Props {
  services: Service[];
}

export default function Services({ services }: Props) {
  if (!services || services.length === 0) {
    return null;
  }

  return (
    <section className="bg-gray-50 px-6 py-16">
      <h2 className="text-3xl font-bold text-center mb-10 text-gray-800">خدماتنا</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {services.map((service, index) => (
          <div
            key={index}
            className="bg-white rounded-xl shadow-sm p-6 text-center hover:shadow-md transition"
          >
            <div className="text-4xl mb-3">{service.icon}</div>
            <h3 className="text-xl font-bold mb-2 text-gray-800">{service.name}</h3>
            <p className="text-gray-600 leading-relaxed">{service.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
