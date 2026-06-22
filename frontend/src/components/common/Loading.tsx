/**
 * Loading spinner component
 */

export function Spinner() {
  return (
    <div className="flex justify-center items-center py-8">
      <div className="animate-spin">
        <div className="w-8 h-8 border-4 border-gray-700 border-t-primary rounded-full"></div>
      </div>
    </div>
  );
}

export function SkeletonLoader({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-panel border border-border rounded-lg p-4 animate-pulse">
          <div className="h-4 bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2 mt-2"></div>
        </div>
      ))}
    </div>
  );
}
