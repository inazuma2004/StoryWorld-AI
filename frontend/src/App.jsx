import { useState } from "react";
import LabPanel from "./components/LabPanel";
import StoryForm from "./components/StoryForm";
import StoryViewer from "./components/StoryViewer";

export default function App() {
  const [story, setStory] = useState(null);
  const [tab, setTab] = useState("create");

  return (
    <div className="app">
      <header className="header">
        <h1>StoryWorld AI</h1>
        <p>Créez votre bande dessinée par IA générative</p>
      </header>

      <nav className="tabs" aria-label="Sections de l'application">
        <button
          type="button"
          className={tab === "create" ? "tab active" : "tab"}
          aria-pressed={tab === "create"}
          onClick={() => setTab("create")}
        >
          Créer une histoire
        </button>
        <button
          type="button"
          className={tab === "lab" ? "tab active" : "tab"}
          aria-pressed={tab === "lab"}
          onClick={() => setTab("lab")}
        >
          Laboratoire IA
        </button>
      </nav>

      <main className="container">
        {tab === "create" ? (
          <>
            <StoryForm onStoryGenerated={setStory} />
            {story && <StoryViewer story={story} />}
          </>
        ) : (
          <LabPanel />
        )}
      </main>
    </div>
  );
}
