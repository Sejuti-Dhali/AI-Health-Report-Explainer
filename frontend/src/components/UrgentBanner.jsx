export default function UrgentBanner({ show }) {
  if (!show) return null

  return (
    <div className="mb-6 rounded-2xl border-2 border-red-500 bg-red-50 p-5 shadow-sm">
      <div className="flex items-start gap-4">

        {/* Icon */}
        <div className="flex-shrink-0 w-10 h-10 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-2xl">
          ⚠️
        </div>

        {/* Content */}
        <div className="flex-1">
          <h3 className="text-red-800 font-semibold text-lg leading-tight">
            দ্রুত ডাক্তারের পরামর্শ নিন
          </h3>

          <p className="text-red-700 mt-2 text-[15px] leading-relaxed">
            আপনার রিপোর্টে এক বা একাধিক পরীক্ষার ফলাফল উদ্বেগজনক।
            অনুগ্রহ করে যত তাড়াতাড়ি সম্ভব একজন যোগ্য ডাক্তারের সাথে যোগাযোগ করুন।
          </p>

          <div className="mt-3 text-xs text-red-600 font-medium flex items-center gap-1">
            <span>🩺</span>
            এটা শুধুমাত্র AI ভিত্তিক সতর্কতা — চূড়ান্ত সিদ্ধান্ত ডাক্তারই নেবেন।
          </div>
        </div>

      </div>
    </div>
  )
}