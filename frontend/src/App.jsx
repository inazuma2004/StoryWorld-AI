import { useState } from "react";
import StoryForm from "./components/StoryForm";
import StoryViewer from "./components/StoryViewer";

export default function App() {
  const [story, setStory] = useState(null);

  return (
    <div className="app">
      <header className="header">
        <h1>StoryWorld AI</h1>
        <p>Créez votre bande dessinée par IA générative</p>
      </header>

      <main className="container">
        <StoryForm onStoryGenerated={setStory} />
        {story && <StoryViewer story={story} />}
      </main>
    </div>
  );
}
