export default function SettingsPage() {
  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="font-display text-3xl">Settings</h1>
      <div className="card-surface mt-4 p-4">
        <p style={{ color: "var(--text-secondary)" }}>
          Configure API keys, dashboard preferences, and runtime toggles here.
        </p>
      </div>
    </main>
  );
}
