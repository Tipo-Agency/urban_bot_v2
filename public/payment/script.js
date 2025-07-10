this.pay = function (userData) {
  const payPrice = userData.start_price + userData.price;
  const subPrice = userData.price;
  const subInterval = "Month";
  const subTitle = `${userData.title} - ${userData.price} ₽/мес, Стартовый взнос - ${userData.start_price} ₽ (разово)`;
  const widget = new cp.CloudPayments({
    yandexPaySupport: false,
    applePaySupport: false,
    googlePaySupport: false,
    masterPassSupport: false,
    tinkoffInstallmentSupport: false,
  });

  const firstReceipt = {
    Items: [
      //товарные позиции
      {
        label: subTitle, //наименование товара
        price: payPrice, //цена
        quantity: 1.0, //количество
        amount: payPrice, //сумма
        vat: 20, //ставка НДС
      },
    ],
    taxationSystem: 0, //система налогообложения; необязательный, если у вас одна система налогообложения
    phone: `${userData.phone}`,
  };

  const receipt = {
    Items: [
      //товарные позиции
      {
        label: subTitle, //наименование товара
        price: subPrice, //цена
        quantity: 1.0, //количество
        amount: subPrice, //сумма
        vat: 20, //ставка НДС
      },
    ],
    taxationSystem: 0, //система налогообложения; необязательный, если у вас одна система налогообложения
    phone: `${userData.phone}`,
  };

  const data = {
    //содержимое элемента data
    CloudPayments: {
      phone: `${userData.phone}`,
      CustomerReceipt: firstReceipt, //чек для первого платежа
      recurrent: {
        interval: subInterval,
        amount: subPrice,
        period: 1,
        customerReceipt: receipt, //чек для регулярных платежей
      },
    },
  };

  widget.pay(
    "charge",
    {
      // options
      publicId: window.CLOUDPAYMENTS_PUBLIC_ID,
      accountId: userData.fio,
      invoiceId: userData.userId,
      description: subTitle,
      amount: payPrice,
      currency: "RUB",
      data: data,
      payer: {
        phone: `${userData.phone}`,
      },
    },
    {
      onSuccess: function (options) {
        // success
      },
      onFail: function (reason, options) {
        // fail
        //действие при неуспешной оплате
      },
      onComplete: function (paymentResult, options) {
        if (paymentResult.success === true) {
          fetch(`/api/success`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              userId: userData.userId,
            }),
          });
        }
      },
    }
  );
};

(function init() {
  const userId = new URLSearchParams(window.location.search).get("token");
  if (!userId) {
    return;
  }

  fetch(`/api/user?id=${userId}`)
    .then((res) => res.json())
    .then((data) => {
      pay({ ...data, userId });
    });
})(); 