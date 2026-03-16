import React from "react";
import { useDrugs } from "../../hooks/useDrugs";
import DrugCard from "./DrugCard";
import { Loader2, Inbox } from "lucide-react";

interface DrugGridProps {
  search?: string;
}

function DrugGrid({ search }: DrugGridProps) {
  const { data: response, isLoading, error } = useDrugs({ search });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-slate-500 font-bold animate-pulse">Loading drug catalog...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-100 p-8 rounded-3xl text-center">
        <p className="text-red-600 font-bold">Error loading drugs. Please try again later.</p>
      </div>
    );
  }

  if (!response?.drugs?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-20 bg-slate-50/50 rounded-3xl border-2 border-dashed border-slate-200">
        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
          <Inbox className="w-8 h-8 text-slate-300" />
        </div>
        <h3 className="text-xl font-black text-slate-900">No drugs found</h3>
        <p className="text-slate-500 font-medium mt-1">Try adjusting your filters or search criteria.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {response.drugs.map((drug) => (
        <DrugCard key={drug.id} drug={drug} />
      ))}
    </div>
  );
}

export default DrugGrid;
