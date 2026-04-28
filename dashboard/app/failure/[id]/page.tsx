interface PageProps {
  params: { id: string };
}

export default function FailureDetailPage({ params }: PageProps) {
  return (
    <main className="mx-auto max-w-3xl p-6">
      <h1 className="text-2xl">Failure {params.id}</h1>
      <p className="mt-3 text-slate-300">Detailed autopsy view placeholder.</p>
    </main>
  );
}
