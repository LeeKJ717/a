ktvmaster v1: 1~4권 통합 DB (과학과영성출판사, 이광조)
복원: cat ktvmasterv1q* | gunzip > ktvmaster.sqlite   (원본 sha256 417762e21b9a95be9a72a33c09a39457741c332ce60f517fa0c21ba8a8fd7609 는 gz 기준)
표: files(원고·코드·자료·DB, zlib 압축 BLOB) refs(장별 참고문헌) papers(고유 논문) pdfs pages captions chapters msrows meta
크롤링 병합: python3 ktvmergev1.py (z840 /data/safe/dball2/ktv_db/crawl 의 works를 crawlworks로)
