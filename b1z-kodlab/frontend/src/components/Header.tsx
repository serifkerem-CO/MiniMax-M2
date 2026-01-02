interface HeaderProps {
  activeTab: string
  setActiveTab: (tab: 'kodla' | 'kodlat' | 'b1z') => void
}

export default function Header({ activeTab, setActiveTab }: HeaderProps) {
  return (
    <header className="bg-b1z-gray-800 border-b-2 border-b1z-accent shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-4">
            <div className="text-4xl font-bold">
              <span className="text-b1z-accent glow-b1z">B1Z</span>
              <span className="text-b1z-white"> KODLAB</span>
            </div>
            <div className="hidden md:block text-sm text-b1z-gray-500 border-l-2 border-b1z-gray-700 pl-4">
              <p className="font-bold">Kodla, Kodlat, B1Z Ol</p>
              <p className="text-xs">Powered by MiniMax-M2</p>
            </div>
          </div>

          {/* Stats */}
          <div className="flex gap-6 items-center">
            <div className="text-center">
              <p className="text-xs text-b1z-gray-500">Toplam Puan</p>
              <p className="points-1111">1111</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-b1z-gray-500">Level</p>
              <p className="text-b1z-accent font-bold text-xl">11</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-b1z-gray-500">Streak</p>
              <p className="text-b1z-white font-bold text-xl">🔥 11</p>
            </div>
          </div>
        </div>

        {/* Slogan */}
        <div className="mt-4 text-center">
          <p className="text-b1z-accent text-sm font-mono animate-pulse-slow">
            [ AI Destekli Kodlama Öğrenme Platformu - 11 Akıl Harmanları ]
          </p>
        </div>
      </div>
    </header>
  )
}
