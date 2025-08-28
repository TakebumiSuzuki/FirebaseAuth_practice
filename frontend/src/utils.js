
export function formatDateToYMD(dateString) {
  // 入力がnullや空文字の場合はそのまま返す
  if (!dateString) {
    return '';
  }

  const date = new Date(dateString);

  // getMonth()は0から始まる（1月が0）ので、1を足す
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const year = date.getFullYear();

  return `${year}-${month}-${day}`;
}