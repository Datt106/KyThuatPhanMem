import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import './home.css';

export default function HomePage() {
  const [items, setItems] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (items.length === 0) return;
    const interval = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % items.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [items]);

  if (items.length === 0) {
    return (
      <div className="home-page">
        <Navbar />
        <div className="no-data-container">Không có dữ liệu...</div>
      </div>
    );
  }

  const currentItem = items[currentIndex];

  const goNext = () => setCurrentIndex((currentIndex + 1) % items.length);
  const goPrev = () => setCurrentIndex((currentIndex - 1 + items.length) % items.length);

  return (
  <div className="home-wrapper">
    <div className="home-container">
      <Navbar />
      <div className="hero-slider">
        {items.map((item, index) => (
          <div
            key={item.id}
            className={`hero-slide ${index === currentIndex ? 'active' : ''}`}
          >
            {item.hinhanh && (
              <img
                src={`${import.meta.env.VITE_API_URL}/uploads/${item.hinhanh}`}
                alt="Hero"
              />
            )}
            <div className="hero-text">
              <h2>{item.tieude}</h2>
              <p>{item.noidung}</p>
              <p className="item-date">Ngày đăng: {item.ngay_dang}</p>
            </div>
          </div>
        ))}
        <button className="hero-prev" onClick={goPrev}>
          &lt;
        </button>
        <button className="hero-next" onClick={goNext}>
          &gt;
        </button>
        <div className="hero-indicators">
          {items.map((_, index) => (
            <span
              key={index}
              className={`indicator ${index === currentIndex ? 'active' : ''}`}
              onClick={() => setCurrentIndex(index)}
            ></span>
          ))}
        </div>
      </div>

      <div className="items-grid">
        {items.map((item, index) => (
          <div key={item.id} className="item-card">
            {item.hinhanh && (
              <img
                src={`${import.meta.env.VITE_API_URL}/uploads/${item.hinhanh}`}
                alt="Thong tin"
                className="item-image"
              />
            )}
            <h3 className="item-title">{item.tieude}</h3>
            <p className="item-content">{item.noidung}</p>
            <p className="item-date">Ngày đăng: {item.ngay_dang}</p>
          </div>
        ))}
      </div>
    </div>
  </div>
);
}
