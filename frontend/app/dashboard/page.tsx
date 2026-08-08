import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import UploadCard from "@/components/upload/UploadCard";
import UrlInput from "@/components/upload/UrlInput";
export default function Dashboard() {
  return (
    <main className="min-h-screen bg-[#070B14] flex">
      <Sidebar />

      <section className="flex-1 p-8">
        <Header />

        <div className="mt-8 rounded-3xl border border-dashed border-blue-500 bg-[#0F172A] h-[600px] flex items-center justify-center">
          <h2 className="text-gray-400 text-2xl">
            <UploadCard />
            <div className="mt-8">
    <UrlInput />
</div>
          </h2>
        </div>
      </section>
    </main>
  );
}