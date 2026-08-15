export function AboutPage() {
  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Methodology</p>
        <h1 className="mt-3 font-display text-4xl font-bold text-white">How DeepGuard AI evaluates media</h1>
      </section>
      <div className="grid gap-6 md:grid-cols-2">
        {[
          {
            title: "What is a deepfake?",
            body: "A deepfake is synthetic or manipulated media generated or altered with AI so that a person appears to say or do something that did not occur."
          },
          {
            title: "Image pipeline",
            body: "DeepGuard AI validates the image, detects facial regions, crops likely faces, normalizes them, and applies either a trained classifier or a clearly labeled baseline heuristic."
          },
          {
            title: "Video pipeline",
            body: "The video analyzer samples frames at a configurable rate, scores each sampled frame, and aggregates those signals into an overall prediction while highlighting suspicious timestamps."
          },
          {
            title: "Limitations",
            body: "Deepfake detection is probabilistic. Results depend on media quality, compression, lighting, and the data used to train the model."
          },
          {
            title: "Ethical use",
            body: "Use the tool for awareness, moderation support, and research. Do not use one scan as definitive proof in high-stakes or legal contexts."
          }
        ].map((card) => (
          <div key={card.title} className="glass rounded-[2rem] border border-white/10 p-6 shadow-glass">
            <h2 className="font-display text-2xl text-white">{card.title}</h2>
            <p className="mt-4 text-slate-300">{card.body}</p>
          </div>
        ))}
      </div>
      <p className="rounded-3xl border border-amber-400/20 bg-amber-300/10 p-5 text-sm text-amber-100">
        DeepGuard AI provides an AI-based prediction and should not be treated as definitive proof that media is
        authentic or manipulated.
      </p>
    </div>
  );
}

