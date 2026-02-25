import { CreateJobForm } from "@/components/jobs/create-job-form";

export default function CreateJobPage() {
  return (
    <div className="mx-auto max-w-xl">
      <h1 className="mb-6 font-mono text-lg font-bold uppercase tracking-widest">
        Create Job
      </h1>
      <CreateJobForm />
    </div>
  );
}
