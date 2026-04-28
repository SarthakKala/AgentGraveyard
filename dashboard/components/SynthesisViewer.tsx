export default function SynthesisViewer({ text }: { text: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <h3 className="text-sm text-slate-400">Synthesized Solution</h3>
      <pre className="mt-2 whitespace-pre-wrap text-sm">{text}</pre>
    </div>
  );
}
