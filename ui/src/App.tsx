import { useState } from "react";
import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import "./index.css";
import axios from "axios";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

type Source = {
  doc_no: string;
  rev: string;
  title: string;
  section: string;
  page: number;
  page_end: number;
  passage: string;
  pdf_url: string;
};

type Answer = {
  found: boolean;
  answer: string;
  sources: Source[];
  safety_critical: boolean;
  version_notes: string[];
};

type Status = "idle" | "loading" | "done" | "error";

const sampleQuestions = [
  "What is the recommended coolant concentration for the TX-200 CNC turning centre?",
  "The machine is showing alarm AL-104. What does it mean and what should the operator do?",
  "Who is allowed to remove a lockout lock from a machine?",
  "What is the outer diameter tolerance for the BH-220 bearing housing?",
  "How often should spindle runout be checked, and who does it?",
];

function sourcePages(source: Source) {
  return source.page === source.page_end
    ? `page ${source.page}`
    : `pages ${source.page} to ${source.page_end}`;
}

function SourceCard({ source }: { source: Source }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">
          {source.doc_no} Rev {source.rev}
        </CardTitle>
        <CardDescription className="text-base">
          {source.section}, {sourcePages(source)}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-1">
        <Accordion>
          <AccordionItem value="passage" className="border-b-0">
            <AccordionTrigger className="min-h-11 text-base text-primary">
              Show the exact text
            </AccordionTrigger>
            <AccordionContent>
              <pre className="overflow-x-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-sm">
                {source.passage}
              </pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
        <a
          href={source.pdf_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex min-h-11 items-center font-semibold text-primary underline-offset-4 hover:underline"
        >
          Open the PDF at this page
        </a>
      </CardContent>
    </Card>
  );
}

function AnswerView({ data }: { data: Answer }) {
  if (!data.found) {
    return (
      <Alert className="border-l-8 border-l-slate-500">
        <AlertTitle className="text-xl">Not in the documents</AlertTitle>
        <AlertDescription className="text-base">
          I couldn't find this in the SOPs and manuals I have. Don't guess. Ask
          your shift supervisor or the document owner.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      {data.safety_critical && (
        <Alert className="border-0 bg-[var(--caution)] text-[var(--caution-ink)]">
          <AlertTitle className="text-base font-bold">Safety step</AlertTitle>
          <AlertDescription className="text-base text-[var(--caution-ink)]">
            Confirm with the Safety Officer or your shift supervisor before you
            act on this.
          </AlertDescription>
        </Alert>
      )}
      <Card>
        <CardContent className="pt-6">
          <p className="whitespace-pre-wrap text-xl leading-relaxed">
            {data.answer}
          </p>
        </CardContent>
      </Card>
      {data.version_notes.map((note) => (
        <Alert key={note} className="border-l-4 border-l-primary">
          <AlertDescription className="text-base">{note}</AlertDescription>
        </Alert>
      ))}
      {data.sources.map((source) => (
        <SourceCard
          key={`${source.doc_no}-${source.section}-${source.page}`}
          source={source}
        />
      ))}
    </div>
  );
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [askedQuestion, setAskedQuestion] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function askQuestion(text: string) {
    const trimmed = text.trim();
    if (trimmed.length < 3) return;
    setQuestion(trimmed);
    setAskedQuestion(trimmed);
    setStatus("loading");
    setAnswer(null);
    try {
      const { data } = await axios.post<Answer>("/ask", { question: trimmed });
      setAnswer(data);
      setStatus("done");
      window.scrollTo({ top: 0 });
    } catch (error) {
      const detail = axios.isAxiosError(error)
        ? error.response?.data?.detail
        : undefined;
      setErrorMessage(
        detail || "Can't reach the server. Check your Wi-Fi and try again.",
      );
      setStatus("error");
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    askQuestion(question);
  }

  return (
    <div className="flex min-h-dvh flex-col bg-muted/40">
      <main className="mx-auto w-full max-w-2xl flex-1 space-y-5 px-4 pb-6 pt-6">
        <header>
          <h1 className="text-2xl font-bold leading-tight">
            Ask the documents
          </h1>
          <p className="text-muted-foreground">
            Answers come only from the plant's SOPs and manuals, with the source
            shown.
          </p>
        </header>

        {status === "idle" && (
          <div className="grid gap-3">
            {sampleQuestions.map((sample) => (
              <Button
                key={sample}
                variant="outline"
                className="h-auto min-h-14 justify-start whitespace-normal bg-background px-4 py-3 text-left text-base font-normal"
                onClick={() => askQuestion(sample)}
              >
                {sample}
              </Button>
            ))}
          </div>
        )}

        {status !== "idle" && (
          <p className="text-muted-foreground">{askedQuestion}</p>
        )}

        <div aria-live="polite">
          {status === "loading" && (
            <p className="text-muted-foreground">Searching the documents...</p>
          )}
          {status === "error" && (
            <p className="font-semibold text-destructive">{errorMessage}</p>
          )}
          {status === "done" && answer && <AnswerView data={answer} />}
        </div>
      </main>

      <div className="sticky bottom-0 border-t bg-background px-4 pb-[calc(0.75rem+env(safe-area-inset-bottom))] pt-3">
        <form onSubmit={handleSubmit} className="mx-auto flex max-w-2xl gap-3">
          <Input
            name="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Type your question"
            enterKeyHint="send"
            maxLength={500}
            autoComplete="off"
            aria-label="Your question"
            className="h-14 flex-1 text-base"
          />
          <Button
            type="submit"
            size="lg"
            className="h-14 min-w-24 text-base font-bold"
            disabled={status === "loading"}
          >
            Ask
          </Button>
        </form>
      </div>
    </div>
  );
}
